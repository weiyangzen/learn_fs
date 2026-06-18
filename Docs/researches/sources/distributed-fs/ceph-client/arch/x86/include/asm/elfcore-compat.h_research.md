
# sources/distributed-fs/ceph-client/arch/x86/include/asm/elfcore-compat.h

Purpose: compat ELF core dump layout helpers for x86-64 supporting both i386 and x32 ABIs.

Important APIs and control flow: aliases `compat_elf_gregset_t` to 64-bit user regs for x32-sized compat regsets. Defines `struct i386_elf_prstatus` for the smaller i386 layout. `PRSTATUS_SIZE` and `SET_PR_FPVALID()` choose the correct layout based on `user_64bit_mode(task_pt_regs(current))`.

State, dependencies, and risks: state is current task mode and core-dump status buffers. Dependencies include `asm/user32.h`, ptrace registers, and compat ELF core code. Risks include writing `pr_fpvalid` at the wrong offset, misclassifying x32 versus i386 mode, and ABI-visible core dump layout regressions. Test signals are core dumps from 32-bit and x32 tasks on x86-64.
