# sources/distributed-fs/ceph-client/drivers/iio/chemical/sps30.h

Purpose: private shared header that defines the transport contract between the SPS30 IIO core and its I2C/serial bus wrappers.

Important APIs, types, and functions: `struct sps30_ops` is the bus operation table: start/stop measurement, read measurement words, reset, fan cleaning, read/write auto-cleaning period, and show device information. `struct sps30_state` is the common runtime state shared with transport implementations: a mutex, parent device, measurement state integer, optional private pointer, and `ops`. `sps30_probe()` is declared as the single entry point for transport probes.

Control flow: transport drivers allocate any private bus state, fill an `sps30_ops` instance, then call `sps30_probe(dev, name, priv, ops)`. After that, the core calls the ops under its own mutex for IIO direct reads, sysfs controls, resets, and triggered-buffer reads.

State and persistence: this header documents that `priv` exists mainly for serdev because `dev` driver data is already used for the IIO device. Persistent hardware settings are accessed only through ops; the shared struct itself is volatile.

Dependencies and integration: includes only `linux/types.h` and forward-declares the state shape for chemical SPS30 modules. It is not a public UAPI header; it is a source-local contract under the chemical driver directory.

Risks and test signals: the ops table has no optional-operation markers, so transports must provide every function or the core will dereference NULL. Tests should verify that each transport's ops table is complete, that private state remains valid for the life of the IIO device, and that state changes are serialized by the core mutex.
