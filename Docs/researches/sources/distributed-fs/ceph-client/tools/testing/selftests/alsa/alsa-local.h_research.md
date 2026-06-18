# sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/alsa-local.h

Purpose: public header for ALSA selftest configuration helpers.

Important APIs/types/functions: declares `get_alsalib_config()`, config load/free functions, card lookup, subtree and typed getters, string-array getter, `struct card_cfg_data` with card id, ALSA config pointer, filename, config id, and linked-list pointer, plus global `conf_cards`.

Control flow: no executable flow; used by `conf.c`, PCM tests, and mixer tests.

State and persistence: declares global linked-list state populated by `conf_load()`.

Dependencies/integration: includes `alsa/asoundlib.h` and exposes libasound `snd_config_t` usage to tests.

Risks and test signals: callers share mutable global `conf_cards`; failure to call `conf_free()` leaks configuration nodes.
