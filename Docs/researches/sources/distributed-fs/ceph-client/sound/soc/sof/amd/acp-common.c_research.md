# sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp-common.c

Purpose: AMD ACP shared SOF DSP ops, panic/IPC dump helpers, and machine-driver selection including optional SoundWire matching.

Important APIs/types/functions: `amd_sof_ipc_dump()` prints scratch IPC flags and interrupt status. `amd_get_registers()` and `amd_sof_dump()` read Xtensa oops, panic info, and stack from ACP mailbox/scratch space. `amd_sof_machine_select()` selects ACPI machine tables or SoundWire alt machines and sets firmware/topology names. `sof_acp_common_ops` is the central `snd_sof_dsp_ops` template.

Control flow: machine selection first tries `desc->machines` with `snd_soc_acpi_find_machine()`, then SoundWire selection if enabled. SoundWire matching fetches slave info, compares link address tables, fills `mach_params`, and returns a matching machine. The ops table wires ACP probe/remove, register/block IO, firmware loading/run, IPC, PCM, trace, PM, debugfs, Xtensa arch support, and probe-client registration into SOF core.

State and persistence: no private persistent state beyond mutating `sdev->pdata` machine and file names. Uses `acp_dev_data` from probe for PCI revision and SoundWire context.

Dependencies and integration points: depends on `acp.h`, `acp-dsp-offset.h`, SOF core ops, ACPI machine tables, SoundWire AMD APIs, and Xtensa arch dump helpers.

Risks: SoundWire machine matching relies on ACPI link count and peripheral enumeration. Incorrect scratch offsets or oops header sizes can make dumps misleading; header size is bounded by `EXCEPT_MAX_HDR_SIZE`.

Test signals: successful SOF probe with ACPI or SoundWire machines, IPC timeout dump content, firmware panic dumps, and trace/probe-client registration.
