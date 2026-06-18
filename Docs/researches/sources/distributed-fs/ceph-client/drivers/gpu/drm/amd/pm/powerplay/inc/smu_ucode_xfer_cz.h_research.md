# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu_ucode_xfer_cz.h

## Purpose

`smu_ucode_xfer_cz.h` defines Carrizo-era SMU microcode transfer metadata. It provides the task/job table format used by firmware and driver code to describe save, restore, load, register access, and initialization work. The file is a binary contract for constructing a table of contents and associated task list in memory.

## Important APIs, types, and constants

The job/task constants define a small bytecode. `TASK_TYPE_*` identifies no-op, microcode load/save, register load/save, and initialization tasks. `TASK_ARG_REG_*` selects register spaces such as SMC indirect, MMIO, FCH, and UNB. `TASK_ARG_INIT_*` names initialization targets like the multimedia power log and clock table.

`JOB_*` constants enumerate save/restore jobs for GFX, FCH, UNB, GMC, and GNB. `IGNORE_JOB` and `END_OF_TASK_LIST` provide sentinels for job and task traversal. `SMU_DRAM_REQ_MM_PWR_LOG` gives the firmware-requested DRAM region size for the multimedia power log.

The `UCODE_ID_*`, `UCODE_ID_*_MASK`, and `UCODE_ID_*_SIZE_BYTE` macros enumerate the firmware components available to the transfer logic: SDMA, CP CE/PFP/ME/MEC jump tables, GMCON RENG, RLC segments, and DMCU ERAM/IRAM. `NUM_UCODES` fixes the component count at 14.

`data_64_t` splits a 64-bit address into high/low 32-bit words. `SMU_Task` stores a task type, argument, next-task index, address, and size. `struct TOC` contains a 32-entry job list followed by a flexible task array.

The `METADATA_CMD_*` constants describe embedded metadata operations for register programming, delay, register-space changes, and whether the operation applies on save or load. `SMU_MetaData_Mode0` through `Mode3` describe register address/data/mask payload formats.

## Control flow

No functions are defined here. Runtime code interprets `struct TOC`: select a job index from `JobList`, walk linked `SMU_Task.next` entries until `END_OF_TASK_LIST`, and execute each task according to its type and argument. Metadata commands are interpreted as another compact command stream for register writes, masked writes, polling, delay, or register-space selection.

## State and persistence behavior

The header describes transient transfer state in DRAM plus hardware state modified by tasks. Microcode load/save tasks move firmware blobs to or from addresses identified by `data_64_t`; register tasks save and restore MMIO-like register contents; initialization tasks provision firmware-visible DRAM regions. Persisted effects are whatever the SMU loads into hardware or saves for later restore during power transitions.

## Dependencies and integration points

The file depends only on fixed-width integer types available to the including compilation unit. It integrates with Carrizo SMU boot/resume code, firmware image layout code, and any logic that constructs the TOC from component masks and firmware blob addresses.

It also integrates with the microcode IDs used elsewhere in AMDGPU. The masks must match firmware expectations so the right blobs are loaded, and the size constants must match the packaged firmware image sizes.

## Risks

Task-list corruption can produce firmware loads from the wrong physical address, overrun a firmware image, or execute an unintended register-space operation. `struct TOC` uses a flexible array with no local bounds enforcement, so callers must allocate enough space and validate task indices.

The hard-coded microcode sizes are brittle. If firmware blobs change size without updating the constants or without independent runtime size validation, transfer code can truncate or overrun payloads. Metadata command values are also magic constants; a mismatch with firmware command decoding can cause silent no-ops or destructive register writes.

## Test signals

Test signals include successful Carrizo SMU boot, suspend/resume save/restore, graphics and multimedia firmware component load success, and absence of SMC/firmware load errors. Focused validation should exercise each job type, metadata register modes, and firmware images whose sizes match every `UCODE_ID_*_SIZE_BYTE` constant.
