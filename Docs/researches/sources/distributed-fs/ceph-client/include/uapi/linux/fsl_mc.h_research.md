# sources/distributed-fs/ceph-client/include/uapi/linux/fsl_mc.h

This UAPI header defines the ioctl ABI for Freescale/NXP Management Complex user access. It lets userspace send management commands through an MC portal and receive command status/results.

Important exports include the MC ioctl magic, `struct fsl_mc_command` with a command header and parameter array, and `FSL_MC_SEND_MC_COMMAND`. The structure is intentionally close to the hardware/firmware command format, carrying command IDs, flags/status in the header, and raw command parameters.

Control flow is ioctl based: userspace opens an MC portal device, fills an `fsl_mc_command`, calls the ioctl, the kernel forwards it to MC firmware, and the command buffer is updated with status and output parameters. State lives in MC firmware objects, portal arbitration, and kernel device ownership. Persistence depends on the specific MC command, because some commands create/configure hardware objects.

Dependencies include `linux/ioctl.h`, `linux/types.h`, NXP DPAA2/FSL MC bus drivers, and MC firmware command semantics. Integration points are DPAA2 management tools, DPL/DPCON/DPNI object configuration, networking/storage accelerator setup, and platform provisioning.

Risks include allowing raw firmware commands from insufficiently trusted userspace, command header layout drift, endianness mistakes, firmware-version incompatibility, and persistent hardware misconfiguration. Test signals include MC command roundtrip tests, firmware compatibility tests, permission checks on portal device nodes, negative command status handling, and DPAA2 object lifecycle tests.
