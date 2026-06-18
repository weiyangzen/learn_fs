# sources/distributed-fs/ceph-client/drivers/net/arcnet/com20020-isa.c

Purpose: ISA bus front-end for ARCNET COM20020 chipset devices. It handles module/boot parameters, I/O region reservation, optional IRQ autoprobe, and hands the initialized netdevice to the shared COM20020 core.

Important APIs and functions: `com20020isa_probe()` validates `dev->base_addr`, reserves `ARCNET_TOTAL_SIZE`, checks for empty I/O space, calls `com20020_check()`, performs IRQ autoprobing when no IRQ is supplied, sets card name, and calls `com20020_found(dev, 0)`. `com20020_init()` allocates an ARCNET device, sets node address, uses `com20020_netdev_ops`, fills `arcnet_local` COM20020 parameters (`backplane`, `clockp`, `clockm`, `timeout`, owner), and probes. `com20020_exit()` unregisters and releases IRQ/I/O resources. Built-in `com20020isa_setup()` parses boot arguments.

Control flow: module load creates one device from parameters; probe confirms hardware and may trigger the card to discover IRQ; shared COM20020 code then registers the netdevice and supplies the actual low-level operations. Exit assumes `my_dev` was successfully initialized and unwinds netdev, IRQ, I/O region, and memory allocation.

State and dependencies: state includes module parameters, global `my_dev`, reserved I/O port range, IRQ, node address, and shared COM20020 private fields. Dependencies are ARCNET core, `com20020.h`, ISA I/O ports, IRQ probing, and module parameter parsing. Risks include no base-address autoprobe, fragile legacy IRQ probing, single-device global design, and exit path assumptions. Test signals include valid/invalid I/O base, empty status `0xff`, IRQ 2 to 9 normalization, `com20020_check()` failure, boot parameter parsing, and unload cleanup.
