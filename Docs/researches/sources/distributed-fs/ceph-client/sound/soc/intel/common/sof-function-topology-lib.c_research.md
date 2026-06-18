# sources/distributed-fs/ceph-client/sound/soc/intel/common/sof-function-topology-lib.c

## Purpose
Builds a list of separated SOF SoundWire function topology files based on the card's DAI links, then validates that each firmware topology file exists before returning the list.

## Important APIs, Types, And Functions
`sof_sdw_get_tplg_files()` is exported with GPL visibility. The private `enum tplg_device_id` tracks SDCA jack, SDCA amp, SDCA mic, Intel PCH DMIC, HDMI, and maximum IDs. The helper parses the platform name from `mach->sof_tplg_filename`, scans `card` prelinks, maps DAI-link names such as `SimpleJack`, `SmartAmp`, `SmartMic`, `dmic`, and `iDisp` to function topology filenames, suppresses duplicates with `tplg_mask`, and calls `firmware_request_nowarn()` for existence checks.

## Control Flow, State, And Persistence
The function is request-scoped. It copies `mach_params`, fills caller-provided `tplg_files`, and uses `devm_kasprintf()` so filename memory is device-managed. Unsupported links either abort separated-topology use by returning `0` or are skipped in `best_effort` mode. Missing firmware also returns `0`, signaling fallback to the monolithic topology path rather than a hard probe failure.

## Dependencies And Integration Points
Depends on ASoC card/prelink iteration, firmware loader APIs, SOF machine descriptors, and naming conventions under the topology firmware search path. DMIC filenames include the parsed platform because NHLT blobs vary by platform.

## Risks And Test Signals
Risks include fragile DAI-link substring matching, unsupported DMIC counts other than two or four, the fixed three-character platform parse, and `tplg_files` capacity assumptions owned by the caller. Test signals include machines with mixed SDCA/DMIC/HDMI links, missing firmware fallback logs, and successful topology componentization with `best_effort` both true and false.
