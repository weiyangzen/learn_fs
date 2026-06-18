# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/kobjects.c

## Purpose
Sysfs front end for Speakup runtime configuration under `/sys/accessibility/speakup` and `/sys/accessibility/speakup/i18n`.

## Important APIs, Types, And Functions
`speakup_kobj_init()`/`speakup_kobj_exit()` create and remove kobjects and attribute groups. Show/store handlers cover characters/chartab, keymap, silent state, current synth, direct synth writes, version, punctuation masks, generic variables through exported `spk_var_show()`/`spk_var_store()`, and i18n message groups.

## Control Flow
Reads format protected in-memory state. Writes parse sysfs buffers, validate syntax/ranges, mutate shared Speakup tables or variables under `speakup_info.spinlock`, and log reset/update/reject status. Synth changes call `synth_init()`, and direct writes unescape text before `synth_write()`.

## State And Persistence Behavior
All state is volatile kernel memory: `spk_key_buf`, `spk_characters`, `spk_chartab`, punc masks, registered `var_t` data, selected `synth`, and i18n messages. Character overrides allocate/free strings and survive until reset/unload/reboot.

## Dependencies, Integration Points, Risks, And Test Signals
Depends on kobject/sysfs APIs, i18n, varhandlers, synth lifecycle, and global Speakup locking. Risks are malformed sysfs input, allocation under spinlock, broad mutation of keymaps/chartabs, and in-place unescaping. Test resets, malformed keymaps, variable inc/dec/default, synth switching, direct escaped writes, i18n updates, and cleanup on init failure.
