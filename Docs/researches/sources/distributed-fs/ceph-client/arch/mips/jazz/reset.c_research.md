<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/jazz/reset.c -->
## sources/distributed-fs/ceph-client/arch/mips/jazz/reset.c

### Purpose
`reset.c` provides the Jazz machine restart routine by driving the keyboard controller reset command path directly.

### Important APIs, Types, And Functions
Key helpers are `jazz_write_output()`, `jazz_write_command()`, `jazz_read_status()`, `kb_wait()`, and exported platform hook target `jazz_machine_restart()`.

### Control Flow
Writes spin until the keyboard input buffer is clear, then write either data or command register. `kb_wait()` waits up to half a second using `jiffies`. `jazz_machine_restart()` loops forever sending command `0xd1` and output `0x00` to force reset.

### State, Persistence, And Dependencies
State is the hardware keyboard-controller status/data registers and `jiffies` for timeout. It depends on `jazz_kh` from Jazz platform headers.

### Integration Points
`plat_mem_setup()` assigns `_machine_restart = jazz_machine_restart`, so generic reboot paths call this function for Jazz machines.

### Risks
The restart path intentionally never returns. It assumes the keyboard-controller reset mechanism is present and functional, and it has no fallback if firmware or hardware ignores the command.

### Test Signals
Manual reboot tests on each Jazz machine type, watchdog observation for non-returning behavior, and fault injection for stuck input-buffer status are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/jazz/reset.c -->
