## sources/distributed-fs/ceph-client/arch/x86/boot/apm.c

### Purpose
`apm.c` queries a 32-bit APM BIOS interface during real-mode boot and records connection metadata in `boot_params` for the later kernel.

### Important APIs, Types, And Functions
The exported function is `query_apm_bios()`. It uses `struct biosregs`, `initregs()`, `intcall()`, `X86_EFLAGS_CF`, and `boot_params.apm_bios_info`.

### Control Flow
The function performs APM installation check via `INT 15h AH=53h`, verifies the `"PM"` signature and 32-bit support bit, disconnects any previous interface, requests a 32-bit connection, stores segment/offset/length fields returned by firmware, checks carry for connection failure, then repeats the installation check because some BIOSes expose different flags after connection.

### State, Persistence, And Dependencies
Persistent state is `boot_params.apm_bios_info`, which later APM kernel code can consume. It depends on 16-bit BIOS interrupt services, correct register return conventions, and `CONFIG_X86_APM_BOOT` object inclusion.

### Integration Points
The boot makefile includes `apm.o` when `CONFIG_X86_APM_BOOT` is set. Later APM support uses the saved descriptors to call into firmware from protected mode.

### Risks
APM BIOS implementations are historically inconsistent. The code defensively disconnects and rechecks, but stores returned fields before the carry check, so later consumers must rely on the function result and valid configuration paths. APM is 32-bit only and not relevant to x86_64 boot.

### Test Signals
Test with APM-capable BIOS emulation, no-APM systems, signatures with carry set, BIOSes that lack 32-bit support, and configurations where `CONFIG_X86_APM_BOOT` is disabled.
