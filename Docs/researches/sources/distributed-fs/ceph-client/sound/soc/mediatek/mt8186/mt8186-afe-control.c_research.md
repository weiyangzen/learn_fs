# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-afe-control.c

## Purpose

This file provides MT8186 helper logic for converting ALSA sample rates into hardware field encodings and for allocating per-DAI private data blocks.

## Important APIs, Types, and Functions

Local enums define hardware encodings for general AFE sample rates, PCM rates, TDM rates, and TDM relatch rates. `mt8186_general_rate_transform()` maps standard rates from 8 kHz through 384 kHz, including 11.025/22.05/44.1-family and 352.8 kHz, to general AFE codes. `tdm_rate_transform()` and `pcm_rate_transform()` provide DAI-specific encoding sets. `mt8186_tdm_relatch_rate_transform()` encodes relatch rates. `mt8186_rate_transform()` dispatches to PCM, TDM, or general mapping based on `aud_blk`. `mt8186_dai_set_priv()` devm-allocates a private block, optionally copies initial data into it, and stores it in `afe_priv->dai_priv[id]`.

## Control Flow and State

Rate transforms are pure switch functions except for logging invalid inputs. Invalid rates fall back to a 48 kHz code rather than returning an error. `mt8186_dai_set_priv()` mutates persistent per-device private state and relies on devm lifetime.

## Dependencies and Integration Points

The helpers are declared in `mt8186-afe-common.h` and used by memif prepare/trigger, ADDA/PCM/TDM/SRC style hw_params paths, and DAI registration code. They depend on `dev_err()` for diagnostics and on valid MT8186 DAI IDs.

## Risks

Fallback-to-48 kHz can mask unsupported-rate bugs and program a stream with the wrong hardware code. `mt8186_dai_set_priv()` does not bounds-check `id`, so callers must pass IDs within `MT8186_DAI_NUM`. It also overwrites `dai_priv[id]` without freeing or detecting an existing allocation, although current registration paths call it once per DAI.

## Test Signals

Unit-like coverage can compare all advertised DAI rates against transform outputs. Runtime signals are successful hw_params for PCM, TDM, ADDA, memif, and SRC paths at all supported rates, plus logs for invalid-rate fallbacks during negative testing.
