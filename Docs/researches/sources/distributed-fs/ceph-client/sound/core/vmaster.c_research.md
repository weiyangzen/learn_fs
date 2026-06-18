# sources/distributed-fs/ceph-client/sound/core/vmaster.c

## Purpose

This file implements ALSA virtual master controls. A virtual master exposes a mixer control whose value attenuates or gates one or more existing follower controls while preserving the followers' original callbacks and cached values.

## Important APIs, Types, and Functions

The exported APIs are `_snd_ctl_add_follower()`, `snd_ctl_add_followers()`, `snd_ctl_make_virtual_master()`, `snd_ctl_add_vmaster_hook()`, `snd_ctl_sync_vmaster()`, and `snd_ctl_apply_vmaster_followers()`. Local state is modeled by `struct link_master`, `struct link_follower`, and `struct link_ctl_info`. Core helpers include `follower_init()`, `follower_update()`, `follower_get_val()`, `follower_put_val()`, `master_init()`, `sync_followers()`, and overridden control callbacks for master and followers.

## Control Flow

`snd_ctl_make_virtual_master()` creates a mono mixer kcontrol backed by `link_master` and optional TLV dB metadata. `_snd_ctl_add_follower()` copies an existing follower kcontrol, stores the copy, replaces the live kcontrol's info/get/put/TLV/free callbacks, and links it under the master. Master initialization lazily inspects the first follower to derive type/range and defaults the master value to maximum. Follower gets return cached unattenuated values; follower puts validate and cache requested values, then write attenuated values to the original callback. Master puts validate the new value, read each follower using the old master value, and rewrite each follower using the new master value.

## State and Persistence Behavior

The master persists follower list, derived type/range, current master value, optional TLV array, and an optional hook. Each follower persists a copy of the original control, its current unattenuated values, flags, and a backpointer to the live kcontrol. Freeing the master restores original follower kcontrol contents while preserving list linkage. `SND_CTL_FOLLOWER_NEED_UPDATE` forces refresh from the original control on initialization.

## Dependencies and Integration Points

It depends on ALSA control core, mixer element callbacks, TLV dB metadata, and kcontrol private data/free semantics. Codec and card drivers use it to build "Master" controls over several hardware-specific volume or switch controls.

## Risks

The code assumes follower controls are integer or boolean, have at most two channels, and share compatible range/type semantics; callers are responsible for selecting sane followers. Attenuation assumes max volume is 0 dB and master cannot add gain. Restoring copied kcontrols in `master_free()` is sensitive to control layout changes. Lack of explicit locking means correctness depends on ALSA control core serialization around callbacks.

## Test Signals

Mixer tests should create virtual masters over mono/stereo integer and boolean followers, verify range validation, attenuation at min/max/mid values, hook invocation, TLV exposure, follower cached value preservation, `snd_ctl_sync_vmaster()`, `snd_ctl_apply_vmaster_followers()`, and correct restoration/removal on card teardown.
