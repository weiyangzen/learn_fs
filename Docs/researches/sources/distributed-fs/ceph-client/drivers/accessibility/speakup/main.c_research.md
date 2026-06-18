# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/main.c

## Purpose
Core Speakup console screen-review engine: keyboard command dispatch, VT integration, cursor/review state, spoken character/word/line/screen/window/highlight output, read-all support, and module init/exit.

## Important APIs, Types, And Functions
Exports/defines shared state such as `speakup_console[]`, `spk_key_buf`, `spk_our_keys[]`, `spk_characters[]`, `spk_chartab[]`, punctuation settings, and `spk_mutex`. Key functions include `spk_set_key_info()`, `spk_reset_default_chars()`, `spk_reset_default_chartab()`, many `say_*` review helpers, `spkup_write()`, `speakup_key()`, `keyboard_notifier_call()`, `vt_notifier_call()`, `speakup_init()`, and `speakup_exit()`.

## Control Flow
Init seeds defaults, registers variables, allocates per-console state, creates sysfs, registers ttyio/devsynth/notifiers, selects the initial synth, and starts `speakup_thread`. Keyboard notifications map keycodes through the Speakup keymap, dispatch review or variable commands, then handle normal typing/cursor/lock feedback. VT notifications speak writes/backspaces and maintain cursor state.

## State And Persistence Behavior
Per-console `struct st_spk_t` stores reading/real cursor, windows, shut-up/park flags, and highlight buffers. Global state tracks read-all sentence buffers, cursor timer, key echo, bells, punctuation, and synth selection. Runtime changes are memory-only.

## Dependencies, Integration Points, Risks, And Test Signals
Integrates with VT, keyboard notifiers, fake keyboard, selection, kobjects, devsynth, synth/thread/buffer code, and variable handlers. Main risks are notifier/timer/console races, keymap ordering, and Latin-1-oriented screen parsing. Test module load/unload, all review commands, read-all indexing, cursor modes, window silence, cut/paste, custom keymaps, graphics pause, no-synth and killed-synth states.
