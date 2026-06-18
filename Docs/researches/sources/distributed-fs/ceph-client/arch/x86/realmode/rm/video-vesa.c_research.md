<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/video-vesa.c -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/rm/video-vesa.c

## Purpose
`video-vesa.c` is a real-mode wrapper that includes the shared boot implementation for `video-vesa` so the ACPI wakeup/realmode blob can reuse boot-time BIOS, copy, register, or video-mode code without maintaining a fork.

## Important APIs, types, and functions
The file exports whatever symbols are emitted by the included `arch/x86/boot` source; locally it only contains a preprocessor include directive.

## Control flow
Build flow is textual inclusion: kbuild compiles this file under real-mode flags, the included boot source emits 16-bit routines, and the realmode linker script places the resulting text/data into `realmode.bin`.

## State and persistence behavior
There is no file-local state. Any mutable state belongs to the included boot code, such as BIOS register structures, port-I/O helpers, video-card tables, or copy buffers.

## Dependencies and integration points
It depends on `arch/x86/boot` sources and on `rm/Makefile` supplying `_SETUP`, `_WAKEUP`, and boot include paths so the shared source sees the expected environment.

## Risks and edge cases
The risk is indirect: changes in boot code can affect suspend wakeup real-mode behavior, and link order matters for the video wrappers because VGA/VESA/BIOS probing order is intentional.

## Test signals
Useful signals are successful `realmode.bin` linking, S3 resume video restoration tests, BIOS-call path testing on legacy systems, and objdump checks that the wrapper emits relocation-safe 16-bit code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/video-vesa.c -->
