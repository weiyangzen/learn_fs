# sources/distributed-fs/ceph-client/sound/ppc/burgundy.h

## Purpose

This header provides Burgundy codec register addresses, default initialization constants, output-enable bit masks, headphone-detect masks, and volume offset definitions.

## Important APIs, types, and functions

Macros name input boost/select, gain, per-source volume, capture/output select, mixer volume, master volume, output enable, attenuation, and host-interface registers. Defaults such as `DEF_BURGUNDY_OUTPUTENABLES`, `DEF_BURGUNDY_MORE_OUTPUTENABLES`, and `DEF_BURGUNDY_MASTER_VOLUME` are consumed during codec initialization. Output bits such as `BURGUNDY_HP_LEFT` and detect bits such as `BURGUNDY_HPDETECT_IMAC_UPPER` drive automute.

## Control flow

There is no executable control flow. `burgundy.c` converts these address macros with `BASE2ADDR/ADDR2BASE` and uses the defaults to program startup state.

## State and persistence behavior

The header defines codec state addresses and constants, not software state. The volume offset of 155 is central to converting ALSA 0-100 values into Burgundy hardware volume values.

## Dependencies and integration points

It is included by `burgundy.c` and `powermac.c` includes it for codec-specific declarations through the build unit. It assumes the AWACS codec command transport used by Burgundy access helpers.

## Risks and test signals

Risks are wrong register constants, unsafe default loudness, and incorrect iMac versus PowerMac output masks. Test by comparing register traces against expected startup defaults and exercising all Burgundy controls.
