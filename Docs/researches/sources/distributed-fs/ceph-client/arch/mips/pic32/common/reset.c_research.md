## sources/distributed-fs/ceph-client/arch/mips/pic32/common/reset.c

### Purpose
This file installs PIC32 restart, halt, and poweroff hooks. It implements software reset through the PIC32 reset register and a halt loop using the MIPS `wait` instruction.

### Important APIs, Types, And Functions
`pic32_halt()` disables forward progress with repeated `wait`. `pic32_machine_restart()` maps `PIC32_BASE_RESET + PIC32_RSWRST`, unlocks SYSKEY, writes and reads the reset bit, then halts. `pic32_machine_halt()` disables interrupts and halts. `mips_reboot_setup()` assigns `_machine_restart`, `_machine_halt`, and `pm_power_off`.

### Control Flow
At `arch_initcall()`, reboot hooks are registered. Restart later maps the reset register, performs the documented magic write/read after `pic32_syskey_unlock()`, and falls back to halt if reset does not complete.

### State, Persistence, And Dependencies
Persistent state is the global machine hook assignments and hardware reset request. Dependencies include PIC32 platform-data base addresses, `pic32_syskey_unlock()`, raw MMIO, and MIPS reboot hooks.

### Integration Points
Kernel restart, halt, and poweroff paths call these hooks. `pic32_syskey_unlock()` is implemented by the MZDA config code.

### Risks
The restart path maps the reset register on each call and never unmaps because reset or halt follows. If `pic32_syskey_unlock()` is unavailable or config MMIO is not initialized, restart may fail.

### Test Signals
Validate `reboot`, `halt`, and `poweroff` paths on hardware, and verify reset register write with a debugger or boot counter.
