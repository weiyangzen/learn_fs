# sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi/mpi30_sas.h

Purpose: defines SAS device-information bit fields and the MPI3 SMP passthrough request/reply ABI.

Important APIs/types/functions: `MPI3_SAS_DEVICE_INFO_*` marks SSP/STP/SMP target and initiator capabilities plus the masked device type values for no device, end device, and expander. `struct mpi3_smp_passthrough_request` carries host tag, function, change count, IO unit port, destination SAS address, request SGE, and response SGE. `struct mpi3_smp_passthrough_reply` returns IOC status/log info and response data length.

Control flow: no direct code runs here. Transport and BSG paths populate the passthrough request, attach request/response buffers, post it through the admin queue, and interpret the reply. The app SGL builder has a special SMP passthrough branch that allows at most two SGEs and requires each SMP data buffer to fit within one ioctl SGE.

State and persistence behavior: no persistent state. SAS capability bits are copied from firmware config pages or event payloads into `mpi3mr` target/SAS transport objects; SMP request state lives only for the duration of a posted admin command.

Dependencies and integration points: relies on `struct mpi3_sge_common` from `mpi30_transport.h`. Used by `mpi3mr_transport.c` for SAS expander/phy management and by `mpi3mr_app.c` for user-space SMP passthrough via BSG. SAS device-info constants are also used when classifying target devices and expanders.

Risks and test signals: incorrect device-info interpretation can misclassify expanders, SATA/STP targets, or initiators and break transport topology. SMP passthrough risks include wrong SAS address, oversized buffers, or response truncation. Tests should cover SMP passthrough success/failure IOC statuses, max-size boundary checks, SAS topology refresh with end devices and expanders, and device-info bit combinations seen in firmware pages.
