# sources/distributed-fs/ceph-client/sound/ppc/keywest.c

## Purpose

This file provides a small shared I2C binding layer for PowerMac audio codecs connected through the Keywest/mac-io I2C bus, used by DACA and Tumbler/Snapper.

## Important APIs, types, and functions

`snd_pmac_keywest_init()` registers an I2C driver, records a single global `pmac_keywest` context, scans consecutive adapters for names beginning with `mac-io`, and instantiates a `keywest` I2C client when one was not already created by `i2c-powermac`. `snd_pmac_keywest_cleanup()` unregisters the client and driver. `snd_pmac_tumbler_post_init()` calls the current context's `init_client()` after the I2C client exists.

## Control flow

Initialization refuses concurrent contexts, grabs adapter 0, registers `keywest_driver`, returns immediately if probe already bound a device, otherwise scans adapters and tries `keywest_attach_adapter()`. Probe stores the client in the current context. Cleanup tears down the global context. Tumbler post-init requires a bound client and runs codec-specific initialization.

## State and persistence behavior

Global `keywest_ctx` stores the active audio I2C context and `keywest_probed` remembers that the driver has bound at least once. This intentionally supports only one active PowerMac audio I2C codec context.

## Dependencies and integration points

It depends on Linux I2C core, `i2c-powermac` naming behavior, and `struct pmac_keywest` declarations in `pmac.h`. DACA calls `snd_pmac_keywest_init()` directly; Tumbler/Snapper use this layer plus `snd_pmac_tumbler_post_init()`.

## Risks and test signals

Risks include global singleton conflicts, adapter reference leaks on the `keywest_probed` early return, unsafe logging through `i2c->client` if driver registration fails before a client exists, and assumptions about adapter numbering/names. Test probe deferral, pre-instantiated and manually-instantiated clients, cleanup/reprobe, and DACA/Tumbler coexistence constraints.
