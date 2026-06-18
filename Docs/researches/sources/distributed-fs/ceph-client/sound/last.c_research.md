# sources/distributed-fs/ceph-client/sound/last.c

Purpose: Provides a late boot diagnostic for ALSA by printing the final list of registered sound cards. It is intentionally small and runs after normal sound-card initialization so boot logs show whether ALSA found cards.

Important APIs/types/functions: The single function `alsa_sound_last_init()` uses `snd_card_ref(idx)` and `snd_card_unref(card)` over `SNDRV_CARDS`, printing each card's `longname`. It is registered with `late_initcall_sync()`.

Control flow: At late initcall time, it prints `ALSA device list:`, iterates all card slots, references live cards, prints `#idx: longname`, unreferences them, and counts successes. If no card exists, it prints `No soundcards found.`

State and persistence: It owns no persistent state. It temporarily holds card references during enumeration and only emits kernel log messages.

Dependencies/integration: Depends on ALSA core card registry and Linux initcall ordering. Risks are minimal; the main behavioral dependency is that card `longname` fields must be initialized before this late call. Test signals are boot log lines with the expected card list or the no-card fallback, plus absence of leaked references or initcall failures.
