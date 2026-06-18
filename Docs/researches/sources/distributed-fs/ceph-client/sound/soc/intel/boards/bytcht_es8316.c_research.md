# sources/distributed-fs/ceph-client/sound/soc/intel/boards/bytcht_es8316.c

## Purpose
This Baytrail/Cherrytrail machine driver supports Everest ES8316 codec boards. It handles highly variable board wiring through DMI and ACPI DSM-derived quirks, selects SSP0 or SSP2 routing, controls an external speaker-enable GPIO, and exposes card component metadata for UCM.

## Important APIs, Types, and Functions
`struct byt_cht_es8316_private` owns the MCLK, headset jack, optional speaker GPIO, codec device reference, and cached speaker-enable state. Quirk flags select internal mic mapping, SSP0, mono speaker, and inverted jack detect. `byt_cht_es8316_init()` adds DAPM routes based on quirks, configures `pmc_plt_clk_3` to 19.2 MHz, sets codec sysclk, creates a headset jack, maps button 0 to `KEY_PLAYPAUSE`, and binds jack detection. `byt_cht_es8316_get_quirks_from_dsm()` reads ES83xx DSM mic, speaker, and HP detect settings. Suspend/resume detach and restore jack detection, and resume reasserts the speaker GPIO to work around buggy touchscreen ACPI methods.

## Control Flow and Integration
Probe rewrites the codec name from ACPI, gets a physical codec device reference, applies platform-name fixups, dumps DSM info, chooses quirks in order: DMI, DSM, BYTCR defaults, or generic defaults. It may add a software node property for inverted jack detect before the codec consumes properties. It maps the speaker GPIO on the codec device, builds `components` and possibly `long_name`, switches to SOF naming/PM ops, sets drvdata, and registers the card. Remove releases the GPIO, software node, and codec reference.

## State, Persistence, and Dependencies
Persistent state includes global `quirk`, mutable DAI CPU name for SSP0, codec software-node properties, card component strings, and hardware MCLK/GPIO/jack state. Dependencies include ES83xx DSM helper APIs, ACPI, DMI, GPIO, common clock framework, Atom SST platform, SOF parent detection, and `soc_intel_is_byt()`.

## Risks and Test Signals
Risks include stale global quirk/link mutation, missed `put_device()` or software-node cleanup on probe errors, DSM values that do not match expected enums, and nonexclusive GPIO sharing with touchscreen firmware. Test signals include component strings matching hardware, correct internal/headset mic routing, speaker GPIO transitions during DAPM and resume, jack detect inversion on affected DMI/DSM systems, and working SSP0 BYTCR and SSP2 non-BYTCR playback/capture.
