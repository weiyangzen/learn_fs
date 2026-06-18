<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/arizona-haptics.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/arizona-haptics.c

Purpose: memless force-feedback haptics driver for Wolfson/Cirrus Arizona MFD devices, controlling haptic intensity through regmap and ASoC DAPM.

Important APIs/types/functions: `struct arizona_haptics` holds the MFD pointer, input device, work item, mutex, and intensity. `arizona_haptics_play()` maps FF_RUMBLE magnitude/direction to device intensity and schedules work. `arizona_haptics_work()` writes intensity, enables/disables haptic control, and syncs the `HAPTICS` DAPM pin. `arizona_haptics_close()` cancels work and disables the pin.

Control flow and state: platform probe obtains parent `struct arizona`, configures actuator polarity/type, creates a memless FF input device, and registers it. Playback callbacks avoid direct register and DAPM work in input context by using a workqueue item.

State and persistence behavior: `intensity` is the only runtime playback state. Hardware haptic control and DAPM pin state persist until changed, with close forcing off.

Dependencies and integration points: depends on Arizona MFD core/pdata/registers, regmap, ASoC DAPM, Linux input FF, and platform device registration under `arizona-haptics`.

Risks: playback fails if `arizona->dapm` is unavailable. Workqueue operations are not explicitly locked around `intensity`, so rapid updates rely on simple byte stores and ordered work execution. Error paths can leave partially enabled hardware if later DAPM sync fails.

Test signals: test FF_RUMBLE strong magnitude scaling for both actuator modes, zero magnitude stop, missing DAPM context, close-time cancellation, and register update failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/arizona-haptics.c -->
