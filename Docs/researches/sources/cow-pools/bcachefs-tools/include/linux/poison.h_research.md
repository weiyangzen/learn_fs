# File Research: sources/cow-pools/bcachefs-tools/include/linux/poison.h

This header defines kernel poison pointer and byte constants. It includes list poison values, timer/static entry poison, page poison, slab red-zone/free/in-use poison bytes, journal poison, DMA pool poison, mutex poison, key destroy byte, network/skbuff pointer poisons, BPF/VFS/stack-depot poisons, and optional `POISON_POINTER_DELTA`.

The values are used for debugging invalid object/list usage and freed/uninitialized memory patterns.
