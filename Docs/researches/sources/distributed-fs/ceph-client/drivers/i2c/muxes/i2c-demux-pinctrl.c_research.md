# sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-demux-pinctrl.c

Purpose: pinctrl-based I2C demultiplexer that exposes one logical adapter while switching which physical parent master drives the bus at runtime.

Important APIs/types: `struct i2c_demux_pinctrl_chan` stores parent nodes, active adapter refs, and OF changesets. `struct i2c_demux_pinctrl_priv` stores current channel, bus name, logical adapter, algorithm, and channel array. Sysfs attributes are `available_masters` and writable `current_master`.

Control flow: probe reads at least two `i2c-parent` phandles and `i2c-bus-name`, prepares per-parent changesets marking parents `status = ok`, activates channel 0, and creates sysfs files. Activation applies the changeset, gets the parent adapter, optionally selects the pinctrl state named by `i2c-bus-name`, builds/registers the current logical adapter, and updates `cur_chan`. Changing master deactivates the current adapter, reverts its changeset, drops the parent ref, then activates the requested channel.

State and persistence: active channel, current adapter registration, parent adapter refs, and applied OF changesets persist until channel change or remove.

Dependencies and integration: depends on OF dynamic changesets, pinctrl, platform devices, runtime PM no-callback setup, and I2C core transfer APIs.

Risks: sysfs master switching can disrupt active clients. Failure during changeset or pinctrl selection must revert state correctly. The logical adapter only implements I2C master transfers, not SMBus-specific callbacks. Parent node references and changesets need balanced cleanup.

Test signals: channel switching through sysfs, pinctrl state selection, adapter add/delete on each switch, transfer forwarding to selected parent, invalid channel rejection, and removal cleanup.
