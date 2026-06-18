# sources/distributed-fs/ceph-client/sound/soc/soc-link.c

## Purpose
This file is a thin sequencing and rollback wrapper around machine-driver DAI link callbacks. It centralizes calls into `dai_link->init`, `exit`, PCM `ops`, compressed `compr_ops`, and `be_hw_params_fixup`, while tracking whether a callback was successfully entered so rollback paths do not call unmatched teardown hooks.

## Important APIs, Types, and Functions
The exported compressed-stream APIs are `snd_soc_link_compr_startup()`, `snd_soc_link_compr_shutdown()`, and `snd_soc_link_compr_set_params()`. PCM-side functions are used internally by ASoC core: `snd_soc_link_init()`, `snd_soc_link_exit()`, `snd_soc_link_be_hw_params_fixup()`, `snd_soc_link_startup()`, `snd_soc_link_shutdown()`, `snd_soc_link_prepare()`, `snd_soc_link_hw_params()`, `snd_soc_link_hw_free()`, and `snd_soc_link_trigger()`.

The file relies on marker fields in `struct snd_soc_pcm_runtime` such as `mark_startup`, `mark_hw_params`, `mark_trigger`, and `mark_compr_startup`. The local macros `soc_link_mark_push()`, `soc_link_mark_pop()`, and `soc_link_mark_match()` currently store one active stream pointer per callback class.

## Control Flow
For startup and hw_params, the wrapper calls the link callback if present and only records the marker on success. Shutdown and hw_free accept a `rollback` flag; when rollback is true, they return unless the matching marker was set for the same substream. Trigger handling maps start-like commands to forward callback execution plus marker push. Stop-like commands optionally check the marker during rollback, call the trigger callback, and pop a marker. Compressed startup/shutdown mirror the PCM startup/shutdown pattern.

## State and Persistence
No heap objects are allocated here. Persistent state is limited to runtime marker fields. These fields are reset during successful teardown and protect error unwind paths from invoking callbacks that were never completed.

## Dependencies and Integration Points
This wrapper is called by `soc-pcm.c` as part of open, close, hw_params, hw_free, prepare, trigger, and DPCM BE fixup. It integrates with machine driver callbacks in `struct snd_soc_ops` and `struct snd_soc_compr_ops`.

## Risks and Test Signals
The marker model assumes one marked substream per runtime field; future multi-substream or more complex rollback scenarios would need list-based tracking, which the comments already anticipate. A notable detail is that the stop branch in `snd_soc_link_trigger()` pops `startup` rather than `trigger`, which is worth preserving or reviewing against the surrounding rollback contract. Test signals should cover callback failure at each stage, rollback without prior success, trigger start failure followed by synthesized stop, compressed stream startup/shutdown rollback, and links with missing optional callbacks.
