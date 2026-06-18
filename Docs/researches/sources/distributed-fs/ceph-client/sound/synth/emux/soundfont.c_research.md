# sources/distributed-fs/ceph-client/sound/synth/emux/soundfont.c

## Purpose
Implements ALSA SoundFont patch loading, GUS patch compatibility, preset-zone lookup, and lifecycle management for `struct snd_sf_list`. It accepts OSS-style SoundFont patch records from userspace, constructs in-memory soundfont/sample/zone lists, delegates actual sample storage to driver callbacks, and builds a preset hash for fast voice lookup by bank, preset, note, and velocity.

## Important APIs, Types, and Functions
Public entry points include `snd_soundfont_load()`, `snd_soundfont_load_guspatch()`, `snd_soundfont_search_zone()`, `snd_sf_new()`, `snd_sf_free()`, `snd_soundfont_remove_samples()`, `snd_soundfont_remove_unlocked()`, `snd_soundfont_close_check()`, and exported conversion helpers such as `snd_sf_linear_to_log()`, `snd_sf_calc_parm_hold()`, `snd_sf_calc_parm_attack()`, and `snd_sf_calc_parm_decay()`. Core private helpers are `open_patch()`, `close_patch()`, `load_info()`, `load_data()`, `load_map()`, `load_guspatch()`, `rebuild_presets()`, `add_preset()`, `delete_preset()`, `search_zones()`, `set_sample()`, and list allocators for `snd_soundfont`, `snd_sf_zone`, and `snd_sf_sample`.

## Control Flow
`snd_soundfont_load()` copies a `soundfont_patch_info` header from userspace, validates patch type and length, opens a patch under the preset mutex for `SNDRV_SFNT_OPEN_PATCH`, then requires matching `open_client` for later patch commands. `SNDRV_SFNT_LOAD_INFO` reads one voice-record header plus voice records, optionally rejects/replaces existing instrument zones, creates zones, initializes default parameters when requested, and resolves sample references. `SNDRV_SFNT_LOAD_DATA` validates sample metadata, rebases sample offsets relative to submitted data, allocates a sample, and calls `callback.sample_new()` to store waveform data. `SNDRV_SFNT_MAP_PRESET` creates shared mapping zones that recursively alias one preset/bank/key to another. Closing a patch clears `currsf`/`open_client` and rebuilds the preset table.

GUS patches are handled separately by `snd_soundfont_load_guspatch()`: it parses legacy `patch_info`, creates a shared GUS font, creates one sample and one zone, converts GUS frequency/envelope/pan/mode fields to SoundFont voice parameters, calls the sample callback, then inserts the zone into the preset table.

Voice lookup starts at `snd_soundfont_search_zone()`, which refuses lookup when `presets_locked` is set, searches requested bank/preset, optionally falls back to default bank/preset, and follows mapping zones recursively with a depth cap of five.

## State and Persistence
All persistent runtime state lives in `struct snd_sf_list`: linked soundfont list, current open font, open client id, preset hash table, allocation counters, locked counters, memory usage, callback table, and optional memory header. Soundfont, zone, and sample records persist until explicit removal or `snd_sf_free()`. Sample storage persists outside this file through callback-owned device memory; `mem_used` mirrors `sp->v.truesize`. `snd_soundfont_remove_unlocked()` keeps locked records by counter threshold and deletes newer zones/samples only.

## Dependencies and Integration Points
Depends on Linux user-copy helpers, ALSA core, `sound/soundfont.h`, `seq_oss_legacy.h`, and driver-provided `struct snd_sf_callback` operations. It integrates with synth drivers that need SoundFont patch loading and with `util_mem.c` through `struct snd_util_memhdr` passed into sample callbacks. The preset mutex and spinlock are ALSA SoundFont synchronization contracts used by callers doing atomic voice lookups.

## Risks
The userspace ABI accepts complex variable-length records; validation of lengths, signed fields, and sample-offset rebasing is security-critical. `load_info()` may create zones whose sample pointer is initially unresolved, relying on later rebuild to resolve them. Mapping recursion is bounded but aliasing can still produce surprising instrument selection. Callback failures must roll back newly allocated samples/zones; the GUS path explicitly frees a zone with `kfree(zone)` after it has been inserted into the font list, so error path review should confirm list integrity. State is shared across clients; `open_client` checks and preset locking are important race barriers.

## Test Signals
Useful tests include loading valid and malformed SoundFont records, duplicate shared samples, exclusive/replace write modes, preset mapping recursion and fallback defaults, GUS 8-bit/16-bit loop modes, sample callback failure rollback, remove-unlocked behavior with locked fonts, and concurrent lookup during patch load/removal. Sanitizer/fuzzing value is high around `copy_from_user()` lengths and sample offset validation.
