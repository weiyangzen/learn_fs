# sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/bsc913x_qds.c

## Purpose
`bsc913x_qds.c` registers the Freescale BSC9132 QDS board.

## Important APIs, Types, and Functions
`bsc913x_qds_pic_init()` allocates and initializes a big-endian single-destination MPIC with 256 interrupts. `bsc913x_qds_setup_arch()` emits progress, initializes MPC85xx SMP support when enabled, assigns the primary FSL PCI controller, and logs board identity. The machine definition uses compatible `"fsl,bsc9132qds"`, common device publication, optional FSL PCI bus fixup, MPIC IRQ retrieval, and UDBG progress.

## Control Flow, State, and Persistence
No file-local state persists. MPIC and common platform devices persist through shared subsystems initialized by hooks.

## Dependencies and Integration Points
It depends on MPC85xx common publish devices, MPIC, optional SMP, FSL PCI assignment/fixup, and BSC9132 QDS DT compatibility.

## Risks and Test Signals
Risks include MPIC allocation failure, missing SMP init on multicore systems, and PCI primary assignment assumptions. Test signals are board boot, MPIC interrupts, SMP bring-up, PCI enumeration/fixups, and platform device publication.
