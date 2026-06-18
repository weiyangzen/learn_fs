# sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/Makefile

Purpose: builds the SGI GRU driver as a composite object.

Important build rules: `ccflags-$(CONFIG_SGI_GRU_DEBUG) := -DDEBUG` enables debug code. `obj-$(CONFIG_SGI_GRU) := gru.o` and `gru-y` links `grufile.o`, `grumain.o`, `grufault.o`, `grutlbpurge.o`, `gruprocfs.o`, `grukservices.o`, `gruhandles.o`, and `grukdump.o`.

Control flow/state: no runtime logic, but it defines which subsystem pieces form `gru.o`.

Dependencies and integration points: requires all listed SGI GRU source files and their x86 UV-platform dependencies.

Risks and test signals: build with and without `CONFIG_SGI_GRU_DEBUG`; link tests should catch missing symbols between researched files and non-researched companion files.
