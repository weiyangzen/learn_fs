# sources/cloud-native/ostree/man/ostree-admin.xml

Purpose: documents the `ostree admin` command group for managing bootable operating-system deployments.

Important APIs/types: command synopsis with `ostree admin [OPTIONS] SUBCOMMAND`; command family includes deploy, upgrade, status, switch, set-origin, cleanup, pin, undeploy, unlock, init/stateroot, and installer utilities.

Control flow: dispatcher documentation rather than one operation; it frames subcommands that read or mutate the sysroot and deployment set.

State and persistence: admin subcommands generally manage persistent sysroot, deployment, origin, bootloader, `/etc`, `/var`, and repository state.

Dependencies and integration: top-level manual page tying together all `ostree-admin-*` pages and CLI group help.

Risks and test signals: risk is index/summary drift as subcommands are added or renamed. Signals are generated help/man consistency and complete cross-links in docs.
