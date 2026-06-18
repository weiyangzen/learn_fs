<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/simple_card.h -->
# sources/distributed-fs/ceph-client/include/sound/simple_card.h

## Purpose
`simple_card.h` declares the legacy/simple ASoC machine-card configuration structure built on top of simple-card utilities.

## Important APIs, types, and functions
`struct simple_util_info` stores card name strings, codec/platform identifiers, DAI format, and CPU/codec `simple_util_dai` descriptions.

## Control flow
Simple-card style machine drivers populate `simple_util_info` or derive equivalent data from firmware. The simple-card probe path uses the CPU/codec DAI data and format to create an ASoC card and DAI link.

## State and persistence behavior
The structure is configuration data only. Runtime card, DAI, jack, and DAPM state lives in the ASoC card and simple utility private structures.

## Dependencies and integration points
It includes `soc.h` and `simple_card_utils.h`, making it a small wrapper around the shared simple-card helper layer.

## Risks and test signals
Risks include incomplete CPU/codec/platform names, unsupported DAI format, and mismatch between static data and firmware-described links. Test signals include simple single-link cards, codec/platform omission handling, and DAI format propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/simple_card.h -->
