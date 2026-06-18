# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmc/pmc.h

Purpose: `pmc.h` is the shared header for AMD PMC core, quirks, and STB helpers.

Important APIs, types, and functions: it defines PMC SMU registers, scratch registers, STB marker constants, mapping sizes and SMU base registers, response codes, FCH S0i3 offsets, SMU message IDs, supported CPU/root-device IDs, `enum s2d_msg_port`, `struct amd_mp2_dev`, `struct stb_arg`, `struct amd_pmc_dev`, IP bitmap and metrics-table structures, and prototypes for quirks, MP2 STB, MP1 STB, and `amd_pmc_send_cmd()`.

Control flow: not executable, but it encodes the register and message contract used by all PMC components. `amd_pmc_dev.msg_port` controls whether `amd_pmc_send_cmd()` uses normal PMC registers or S2D STB registers.

State and persistence: structure definitions describe runtime state such as MMIO mappings, root PCI device reference, active IP bitmaps, SMU version, debugfs root, quirks, MP2 pointer, and STB arguments. No state is instantiated here.

Dependencies and integration points: includes Linux types and mutex. It bridges core PMC, DMI quirks, MP1 STB, and MP2 STB into one composite module.

Risks: register constants are hardware-specific; mistakes affect suspend/resume firmware commands. Shared `amd_pmc_dev` fields create coupling between normal PMC and STB code, especially `msg_port` and `stb_arg`. CPU ID definitions overlap with root PCI IDs and must remain synchronized with probe tables.

Test signals: compile coverage of all consumers, correct SMU command offsets per CPU family, STB S2D command routing, and structure layout compatibility across composite object files.
