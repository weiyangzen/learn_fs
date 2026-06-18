## sources/distributed-fs/ceph-client/arch/x86/boot/Makefile

### Purpose
`arch/x86/boot/Makefile` builds the real-mode setup code and wraps the compressed kernel into `bzImage` plus optional legacy disk, hard disk, and ISO images.

### Important APIs, Types, And Functions
Important variables include `SVGA_MODE`, `targets`, `setup-y`, `SETUP_OBJS`, `KBUILD_CFLAGS`, `KBUILD_AFLAGS`, `sed-zoffset`, `OBJCOPYFLAGS_vmlinux.bin`, `LDFLAGS_setup.elf`, `FDARGS`, `FDINITRD`, and `imgdeps`. Build rules generate `cpustr.h`, `zoffset.h`, `setup.elf`, `setup.bin`, `vmlinux.bin`, `compressed/vmlinux`, `bzImage`, `mtools.conf`, and image formats through `genimage.sh`.

### Control Flow
The makefile compiles real-mode setup objects with exported `REALMODE_CFLAGS`, optionally adds `apm.o`, orders video drivers deliberately, builds the compressed kernel subdirectory, extracts symbol offsets from compressed `vmlinux` into `zoffset.h`, links setup code with `setup.ld`, objcopies setup and compressed images to binaries, and concatenates synchronized setup plus compressed payload into `bzImage`.

### State, Persistence, And Dependencies
Build state lives in generated setup binaries, compressed image objects, generated headers, and image artifacts. Dependencies include real-mode C/assembly helpers, `arch/x86/boot/compressed`, `mkcpustr`, `nm`, `sed`, `objcopy`, linker scripts, `mtools.conf.in`, and `genimage.sh`.

### Integration Points
The top-level x86 makefile calls this makefile for `bzImage` and legacy image targets. Runtime setup code produced here populates `boot_params`, enters protected mode, and passes control to compressed kernel startup.

### Risks
The setup image is size and ABI constrained. `sed-zoffset` must track symbols required by the boot header. Video object order is intentional, and changing it can alter mode probing. Legacy image targets depend on external tools such as syslinux and, for EFI hard-disk images, OVMF/EDK2.

### Test Signals
Build `arch/x86/boot/bzImage`, inspect generated `zoffset.h`, boot under BIOS and EFI test environments, and exercise legacy image targets when their external tools are installed.
