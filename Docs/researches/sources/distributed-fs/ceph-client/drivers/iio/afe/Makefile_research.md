# sources/distributed-fs/ceph-client/drivers/iio/afe/Makefile

## Purpose
This Makefile maps the IIO AFE rescale Kconfig symbol to its object file.

## Important APIs, Types, And Functions
The only build rule is `obj-$(CONFIG_IIO_RESCALE) += iio-rescale.o`.

## Control Flow
Kbuild expands the rule to built-in, module, or empty based on the `IIO_RESCALE` tristate value.

## State And Persistence
There is no runtime state. The file contributes to the persistent build graph.

## Dependencies And Integration Points
It integrates with `drivers/iio/afe/Kconfig` and kbuild. The comment asks maintainers to keep entries alphabetical, which is trivial while only one object exists.

## Risks And Test Signals
Risks are stale object names after file renames or missing rules when new AFE drivers are added. Test signals are successful `M=drivers/iio/afe` builds with `CONFIG_IIO_RESCALE=m` and no orphaned Kconfig symbols.
