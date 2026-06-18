# sources/distributed-fs/ceph-client/sound/soc/codecs/bt-sco.c

## Purpose
`bt-sco.c` is a generic ASoC codec shim for Bluetooth SCO links. It has no hardware register control; it declares DAPM endpoints and DAIs so machine drivers can connect CPU audio links to Bluetooth SCO PCM.

## Important APIs, Types, And Functions
The driver exposes DAPM widgets `RX`, `TX`, `BT_SCO_RX`, and `BT_SCO_TX`, with routes from physical RX to capture AIF and playback AIF to TX. It registers two DAIs: `bt-sco-pcm` for narrowband 8 kHz mono S16_LE playback/capture and `bt-sco-pcm-wb` for 8 or 16 kHz mono S16_LE. `bt_sco_probe()` simply registers the component and both DAIs.

## Control Flow And State
There is no mutable driver state. Platform probe registers the component; all runtime behavior is handled by ASoC DAPM and PCM constraints.

## Dependencies And Integration Points
The driver binds through platform IDs `dfbmcs320` and `bt-sco`, and OF compatibles `delta,dfbmcs320` and `linux,bt-sco`. It integrates with machine drivers needing a codec-side endpoint for Bluetooth controllers.

## Risks And Test Signals
The main risk is mismatched machine-driver DAI name or rate selection. There is no power sequencing or format programming. Test signals are component registration, DAPM route visibility, and successful PCM open at 8 kHz or 16 kHz wideband on the expected DAI.
