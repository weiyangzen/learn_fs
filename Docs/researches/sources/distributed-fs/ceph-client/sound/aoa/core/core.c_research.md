# sources/distributed-fs/ceph-client/sound/aoa/core/core.c

## Purpose

This file coordinates AOA codec and fabric registration. It enforces the single-fabric model, keeps the global codec list, attaches codecs to the active fabric, and manages module references and ALSA card lifetime.

## Important APIs, types, and functions

Public exports are `aoa_codec_register`, `aoa_codec_unregister`, `aoa_fabric_register`, `aoa_fabric_unregister`, and `aoa_fabric_unlink_codec`. Internal state is `fabric` and `codec_list`. `attach_codec_to_fabric()` is the core attach sequence.

## Control Flow

When a codec registers, it is attached immediately if a fabric exists, then added to the list. Fabric registration creates the ALSA card, stores the fabric, and walks existing codecs for attachment. Attachment gets the codec module, calls fabric `found_codec`, sets `c->fabric`, calls codec `init`, and notifies `attached_codec`. Failures call fabric `remove_codec` and release the module reference. Fabric unregister unlinks all attached codecs and cleans up the ALSA card.

## State and Persistence

The global fabric pointer and codec list persist for module lifetime. Codec structs are owned by codec drivers. Module references are held while codecs are attached to a fabric.

## Dependencies and Integration Points

It depends on AOA header contracts and ALSA helper initialization. Codecs and fabrics use these exported functions to rendezvous.

## Risks and Test Signals

Risks include no explicit locking around `codec_list` and `fabric`, module_put on unregister paths for codecs never attached, attach failure ordering, and single-fabric/card limitations. Tests should cover codec/fabric registration order, attach failures, unregister ordering, and repeated fabric registration.
