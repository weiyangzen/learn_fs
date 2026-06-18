# sources/distributed-fs/ceph-client/drivers/media/tuners/xc2028-types.h

Purpose: internal firmware type and extended V4L2 audio-standard bit definitions for Xceive firmware selection.

APIs/constants: defines firmware flags `BASE`, `F8MHZ`, `MTS`, `D2620`, `D2633`, `DTV6/7/78/8`, `QAM`, `FM`, input bits, `LCD`, `NOGD`, `INIT1`, SCODE bits, and `HAS_IF`; masks group base, DTV, standard-specific, and SCODE types. Also defines internal audio bits and combinations such as A2/NICAM/BTSC/EIAJ variants.

Control flow/state: no state. XC2028/XC4000 firmware loaders use these masks to parse firmware containers, seek best matches, and choose base/std/scode segments.

Dependencies/integration: relies on V4L2 standard bit layout and binary firmware format.

Risks/tests: bit collisions or mask errors cause wrong firmware loading. Test analog audio-standard selection, DTV bandwidth firmware selection, SCODE and `HAS_IF` matching.
