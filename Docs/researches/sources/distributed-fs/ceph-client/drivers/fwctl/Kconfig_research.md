# sources/distributed-fs/ceph-client/drivers/fwctl/Kconfig

## Purpose
This Kconfig file introduces the fwctl firmware-access framework and its first device-specific providers. The framework is intended to provide a restricted userspace path for device firmware communication that does not fit existing subsystems.

## Important Entries
`FWCTL` is the top-level tristate menuconfig. Provider symbols are `FWCTL_BNXT`, `FWCTL_MLX5`, and `FWCTL_PDS`, depending respectively on `BNXT`, `MLX5_CORE`, and `PDS_CORE`.

## Control Flow and State
There is no runtime code. Kconfig selection controls whether the core `fwctl` module and each auxiliary-bus provider module are built.

## Dependencies and Integration Points
The entries integrate with NIC core drivers that create auxiliary devices. The runtime subsystem also relies on uapi headers under `uapi/fwctl`.

## Risks and Test Signals
The top-level help text describes powerful firmware operations including flash manipulation and debugging, so build enablement should be reviewed with lockdown and privilege expectations. Tests are mainly configuration matrix builds: core alone, each provider as built-in or module, and provider symbols disabled when their parent NIC symbols are absent.
