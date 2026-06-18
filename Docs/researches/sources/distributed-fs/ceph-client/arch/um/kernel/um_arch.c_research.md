# sources/distributed-fs/ceph-client/arch/um/kernel/um_arch.c

## Purpose
Owns UML architecture boot setup: command-line normalization, host CPU/capability reporting, memory layout calculation, panic behavior, architecture setup, text-patching stubs, and suspend integration.

## Important APIs, Types, and Functions
`linux_main()` parses UML setup options, adds default `root=`/`console=`, computes `stub_start`, `task_size`, physical/vmalloc layout, reads host CPU features, and enters `start_uml()`. `setup_arch()` initializes physical memory, DTB/initrd, command line, host info, CPU map, and RNG seed. `uml_finishsetup()` registers panic notifier and postsetup calls. `cpuinfo_op` backs `/proc/cpuinfo`. PM hooks implement suspend-to-mem through UML idle sleep.

## Control Flow, State, and Persistence
Boot-time globals include `command_line`, `host_info`, `uml_physmem`, `uml_reserved`, `physmem_size`, `start_vm`, `end_vm`, `stub_start`, `task_size`, and `brk_start`. These are initialized before SMP and remain effectively stable. Panic exits dump kmsg and core.

## Dependencies and Integration Points
Integrates with host early checks, physical memory setup, initrd/DTB hooks, CPU feature parsing from `start_up.c`, signal wake support, suspend core, and x86 text-patching call sites that UML mostly stubs out.

## Risks and Test Signals
Risks are address-layout miscalculation, command-line overflow, insufficient vmalloc/physmem space, host CPU flag parsing drift, and suspend wake behavior in time-travel mode. Test varied argv/envp sizes, `mem=`, default root/console, `/proc/cpuinfo`, panic, suspend, and ASLR-disabled reexec.
