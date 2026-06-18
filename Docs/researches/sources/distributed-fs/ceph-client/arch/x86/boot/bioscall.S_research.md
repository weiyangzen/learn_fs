## sources/distributed-fs/ceph-client/arch/x86/boot/bioscall.S

### Purpose
`bioscall.S` implements the real-mode `intcall()` trampoline used by C setup code to invoke BIOS interrupts while protecting the boot C environment from register and segment clobbering.

### Important APIs, Types, And Functions
The single exported symbol is `intcall`. The ABI matches `void intcall(u8 int_no, const struct biosregs *ireg, struct biosregs *oreg)`. It operates in `.code16` and uses the `struct biosregs` stack layout defined in `boot.h`.

### Control Flow
`intcall` self-modifies the interrupt vector byte in an `INT` instruction, saves flags, FS/GS, and general registers, copies the caller's input register image to a stack frame, restores full register state from that frame, executes the selected BIOS interrupt, pushes the post-interrupt state, reestablishes C invariants such as direction flag, DS, ES, and 16-bit stack shape, optionally copies the output state to the caller, then restores saved state and returns.

### State, Persistence, And Dependencies
Persistent state is limited to the modified interrupt immediate byte inside the function. It depends on real-mode execution, writable/executable boot text, the exact `biosregs` layout, and C callers passing segment-addressable pointers.

### Integration Points
BIOS users such as A20, APM, memory, EDD, video, and other setup helpers call `intcall()` to perform firmware services before protected-mode handoff.

### Risks
Self-modifying code and register-frame layout are fragile. Any `struct biosregs` layout change must be mirrored here. BIOSes may still corrupt memory or behave asynchronously, but this wrapper prevents common register/segment damage from leaking into C code.

### Test Signals
Exercise BIOS calls that return no output and calls that populate output registers, check segment registers after calls, and boot on emulators with BIOS services for APM/video/memory probing.
