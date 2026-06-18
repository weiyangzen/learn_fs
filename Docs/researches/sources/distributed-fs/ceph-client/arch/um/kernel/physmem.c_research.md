# sources/distributed-fs/ceph-client/arch/um/kernel/physmem.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/physmem.c -->
## sources/distributed-fs/ceph-client/arch/um/kernel/physmem.c

### Purpose
This file creates and maps UMLs host-backed physical memory file.

### Important APIs, Types, And Functions
It defines `physmem_fd`, exported `high_physmem`, `map_memory()`, `setup_physmem()`, exported `phys_mapping()`, and `mem=` setup parsing.

### Control Flow
`setup_physmem()` validates the requested memory, creates a backing file, maps memory after the executable image, writes the syscall stub page into the backing file, registers/reserves memblock ranges, and sets low PFN bounds. `phys_mapping()` maps physical offsets to the backing fd.

### State, Persistence, And Dependencies
Persistent state is the backing fd, host mappings, memblock records, `high_physmem`, PFN bounds, and `physmem_size`. Dependencies include host memory-file/mmap wrappers, linker symbols, memblock, address conversion macros, and syscall stub sections.

### Integration Points And Risks
Risks include host `vm.max_map_count` failures, too-small `mem=`, backing-file visibility limits for DMA, and single-range assumptions. Integration feeds SKAS, vhost-user, VFIO, and generic memory management.

### Test Signals
Boot with varied `mem=`, trigger low-memory failure, validate vhost/VFIO memory mapping, and execute syscall stub paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/physmem.c -->
