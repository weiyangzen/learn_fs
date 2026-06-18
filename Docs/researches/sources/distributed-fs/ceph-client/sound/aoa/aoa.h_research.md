# sources/distributed-fs/ceph-client/sound/aoa/aoa.h

## Purpose

This is the central Apple Onboard Audio public header. It defines the codec/fabric registration contracts, shared ALSA helper entry points, and exported GPIO method providers.

## Important APIs, types, and functions

Key types are `struct aoa_codec`, `struct aoa_fabric`, and `struct aoa_card`. Important APIs are `aoa_codec_register`, `aoa_codec_unregister`, `aoa_fabric_register`, `aoa_fabric_unregister`, `aoa_fabric_unlink_codec`, `aoa_snd_device_new`, `aoa_get_card`, and `aoa_snd_ctl_add`. It also declares `pmf_gpio_methods` and `ftr_gpio_methods`.

## Control Flow

The header specifies that codecs register independently, a fabric later claims codecs through `found_codec`, fills soundbus/GPIO/connection fields, calls codec `init`, and then receives `attached_codec`. Removal flows through codec `exit` and fabric `remove_codec`.

## State and Persistence

`aoa_codec` instances store codec name, owner, OF node, assigned soundbus device, GPIO runtime, connection bitmask, fabric data, list linkage, and fabric pointer. `aoa_fabric` stores callbacks and module ownership. `aoa_card` wraps one ALSA card.

## Dependencies and Integration Points

It depends on ALSA core/control headers, modules, AOA GPIO, and soundbus definitions. Codecs, core, fabric, and soundbus all share this contract.

## Risks and Test Signals

Risks include single-card/single-fabric assumptions, module reference imbalance, codec fields being used before fabric assignment, and connection bit meanings differing by codec. Tests should cover codec-before-fabric and fabric-before-codec registration, unregister ordering, and multiple codec layouts.
