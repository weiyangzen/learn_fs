# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vcn.h

## Purpose

`amdgpu_vcn.h` is the central VCN contract for modern AMD video decode/encode blocks. It defines command opcodes, DPG register access macros, firmware shared-memory layouts, per-instance and device-level state, RAS/debug structures, codec disable flags, ring types, and common lifecycle/test/RAS/reset APIs.

## Important Types And Data

The header defines VCN stack/context sizes, firmware offset, maximum encode rings and instances, harvest flags, decode/encode command ids, DPG LMA read/write macros for SOC15/SOC24, firmware shared capability flags, codec disable masks, SMU DPM interface ids, and DRM-key workaround constants.

`struct amdgpu_vcn_inst` is the main per-instance state: device/instance ids, VCPU BO, saved BO, decode and encode rings, scheduler score, IRQ and RAS poison IRQ sources, register mappings, DPG SRAM BO and cursor, pause state, firmware shared memory metadata, codec config, submission counters, power-gating locks/state, delayed idle work, firmware version, encode ring count, indirect SRAM flag, internal registers, workaround locks, callbacks for DPG pause/power/reset, unified-queue flag, and reset mutex.

`struct amdgpu_vcn` stores device-level instance count, instance array, harvest mask, RAS block pointers, instance masks, register dump buffer/list, supported reset mask, caps, firmware sharing mode, workload profile state, and register counts. Firmware shared structs describe VCN3, VCN4, and VCN5 memory contracts for queue modes, firmware logging, ring buffer setup, DRM key workaround, queue decoupling, RB metadata, decode buffers, and SMU interface data.

Exports include early/software init/fini, suspend/resume, ring begin/end, disabled-queue tests, decode/encode/unified ring tests, priority mapping, PSP SRAM update, firmware log/debugfs setup, RAS init/poison handling, sysfs/debugfs controls, powergating, ring reset, register dumps, and workload profile management.

## Control Flow And Integration

IP-version-specific code fills the register and callback fields, then common VCN code handles firmware memory, power transitions, tests, debugfs/sysfs, and RAS. The DPG macros are used by hardware blocks to access internal VCN registers while power-gated. Firmware shared-memory structs are written into the VCPU BO region and consumed by firmware, so layout compatibility is critical.

Dependencies include `amdgpu_ras.h`, AMDGPU register macros, BO/ring/job types, debugfs/sysfs, PSP firmware loading, reset logic, and DRM printer/debug infrastructure.

## State, Risks, And Tests

State is GPU-BO backed, firmware-shared, and per-instance. Risks include ABI drift in firmware shared structs, unbounded assumptions about instance/ring counts, incorrect harvest masking, callback null dereferences, DPG macro misuse, and debugfs/sysfs access after teardown. Test signals include build coverage for all macro users, struct layout validation against firmware expectations, init/fini across harvested instances, unified versus split queue behavior, codec disable masks, reset mask reporting, and RAS/debug paths.
