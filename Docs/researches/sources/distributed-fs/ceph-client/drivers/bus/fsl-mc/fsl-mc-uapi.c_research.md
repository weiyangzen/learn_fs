# sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/fsl-mc-uapi.c

Purpose: exposes a controlled userspace miscdevice for sending selected Management Complex commands to the root DPRC. It allows management tooling to query or modify MC resources while filtering the command set and requiring `CAP_NET_ADMIN` for resource-changing operations.

Important APIs and types: `struct uapi_priv_data` binds an open file to a `fsl_mc_uapi` and an MC portal. `struct fsl_mc_cmd_desc` describes accepted command IDs, masks, payload sizes, token expectations, and security flags. Public internal entry points are `fsl_mc_uapi_create_device_file()` and `fsl_mc_uapi_remove_device_file()`.

Control flow: miscdevice open serializes access to a static root portal for the first opener, otherwise allocates a dynamic DPMCP portal. `FSL_MC_SEND_MC_COMMAND` copies a full `struct fsl_mc_command` from userspace, calls `fsl_mc_command_check()`, sends it through `mc_send_command()`, and copies the response back. Release returns dynamic portals or clears the static-in-use flag.

State and persistence: per-open state is heap allocated and released on close. The shared `local_instance_in_use` flag protects the static portal. No persistent state is written, but accepted commands can change MC firmware object state.

Dependencies and integration: depends on FSL MC command header decoding, portal allocation, miscdevice, copy_from/to_user, Linux capabilities, and root `fsl_mc_bus` lifetime. It integrates with `fsl_mc_bus` only when UAPI support is enabled.

Risks: the allowlist is the primary security boundary. Size checks require all unused bytes past a command's declared size to be zero, token presence must match the command, and generic CREATE/DESTROY/OPEN/API_VERSION commands validate module IDs. Incorrect allowlist sizes or masks could permit malformed firmware commands; dynamic portal allocation failures limit concurrent opens. Test signals include accepted/rejected command IDs, garbage tail rejection, token mismatch rejection, CAP_NET_ADMIN gating, concurrent opens, portal release, and ioctl copy fault handling.
