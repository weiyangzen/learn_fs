# Research Group subset-b-001009

This grouped report covers the requested Speakup console speech sources under `sources/distributed-fs/ceph-client/drivers/accessibility/speakup`. Each section preserves the source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/kobjects.c -->
# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/kobjects.c

## Purpose

`kobjects.c` exposes Speakup runtime configuration through `/sys/accessibility/speakup` and `/sys/accessibility/speakup/i18n`. It is the sysfs front end for keymaps, character descriptions, character classes, punctuation masks, global numeric/string variables, synthesizer selection, direct synthesizer writes, version reporting, and user-overridable i18n message groups.

## Important APIs, Types, And Functions

The main entry points are `speakup_kobj_init()` and `speakup_kobj_exit()`, which create and remove the `accessibility/speakup` kobjects and sysfs groups. Store/show handlers include `chars_chartab_show/store`, `keymap_show/store`, `silent_store`, `synth_show/store`, `synth_direct_store`, `version_show`, `punc_show/store`, exported `spk_var_show/store`, and message helpers for i18n groups. Attribute arrays `main_attrs` and `i18n_attrs` define the public sysfs ABI.

## Control Flow

Reads format current in-kernel state under `speakup_info.spinlock`. Writes parse sysfs input, validate ranges and syntax, update shared Speakup tables or variables, and report partial updates with `pr_info` or invalid input with `pr_warn`. Synthesizer changes route to `synth_init()`, direct writes unescape user text and call `synth_write()`, and i18n writes use `spk_msg_set()` or reset whole groups.

## State And Persistence Behavior

State is in memory only: `spk_key_buf`, `spk_characters`, `spk_chartab`, punctuation masks, registered `var_t` objects, selected `synth`, and i18n message storage. Character overrides allocate strings and free replaced non-default entries. Sysfs writes persist until reset, module unload, or reboot.

## Dependencies And Integration Points

This file depends on kobject/sysfs APIs, string unescaping, `speakup.h`, `spk_priv.h`, i18n helpers, variable handlers, synthesizer lifecycle, and the global Speakup spinlock. Synthesizer-specific modules reuse exported `spk_var_show()` and `spk_var_store()` for their own per-synth attributes.

## Risks

Input parsing is security-sensitive because sysfs writes can resize character descriptions and mutate keymaps. The code bounds character indices, descriptions, keymap versions, and sysfs buffer lengths, but many updates occur under a spinlock with `GFP_ATOMIC`; allocation failure resets character state. `spk_var_store()` unescapes in place after casting away `const`, so callers must provide mutable sysfs buffers as the kernel sysfs path does.

## Test Signals

Useful checks include reading every sysfs file after init, resetting characters/chartab/keymap with `d` or `r`, rejecting malformed keymaps and out-of-range character indices, changing numeric variables with set/inc/dec/default forms, switching synth names, writing escaped bytes through `synth_direct`, and verifying i18n group reset and partial rejection counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/kobjects.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/main.c -->
# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/main.c

## Purpose

`main.c` is the core Speakup console screen-review engine. It tracks virtual console cursor/review positions, interprets Speakup key bindings, speaks characters, words, lines, sentences, screens, windows, and highlighted text, integrates with keyboard and VT notifiers, owns global user-facing variables, and starts/stops the Speakup kernel thread and synthesizer infrastructure.

## Important APIs, Types, And Functions

Public state includes `speakup_console[]`, `spk_key_buf`, `spk_our_keys[]`, `spk_characters[]`, `spk_chartab[]`, punctuation settings, lock `spk_mutex`, and module params such as `synth`, `quiet`, `bell_pos`, `cursor_time`, and `key_echo`. Key functions include `spk_set_key_info()`, `spk_reset_default_chars()`, `spk_reset_default_chartab()`, `speakup_init()`, `speakup_exit()`, `keyboard_notifier_call()`, `vt_notifier_call()`, review helpers `say_*`, `spell_word()`, `spkup_write()`, `do_spkup()`, `speakup_key()`, and read-all cursor-timer handlers.

## Control Flow

Initialization sets default i18n, characters, chartab, variables, keymap, virtual keyboard, per-console state, sysfs kobjects, tty line discipline, initial synth, devsynth, keyboard/VT notifiers, and `speakup_thread`. Keyboard notifier events first map keycodes through `spk_key_buf`, dispatch Speakup commands, then post-process normal typing, cursor keys, shifts, and lock keys. VT notifier events allocate/free console state, speak writes and backspaces, and update cursor/graphics pause state. Output text is filtered by `spkup_write()` through chartab classes, punctuation masks, repeat detection, and synth buffer helpers.

## State And Persistence Behavior

Per-console `struct st_spk_t` records reading cursor, real cursor, window bounds, parking/shutdown flags, and highlight buffers. Global variables store punctuation behavior, key echo, bell timing, read-all sentence buffers, and cursor timer state. All state is volatile kernel memory; module parameters seed defaults but runtime sysfs/key changes disappear on unload or reboot.

## Dependencies And Integration Points

This file integrates with VT, keyboard notifiers, console screen memory, selection helpers, fake keyboard, i18n, kobjects, devsynth, synth/thread/buffer code, variable handlers, and hardware/software synth modules through `struct spk_synth`. It uses spinlocks for shared Speakup state and a timer for cursor/read-all delayed speech.

## Risks

The code mixes notifier context, timers, console memory access, fake key injection, spinlocks, and synthesizer buffer state. Races around cursor timers, console deallocation, and synth removal are primary risks. Screen parsing is byte/Latin-1 oriented with explicit non-Latin handling only in synth paths. Keymap changes can break command dispatch if validation misses a bad layout.

## Test Signals

Exercise module load/unload, keyboard notifier dispatch, default and custom keymaps, all major review commands, cursor tracking modes, read-all with synth indexing, cut/paste, window silence, punctuation editing, bell position, graphics-mode pause string, VT allocate/deallocate, and operation with no synth, killed synth, and quiet boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/makemapdata.c -->
# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/makemapdata.c

## Purpose

`makemapdata.c` is a host-side generator that scans kernel key definitions and Speakup private key constants to emit a C initializer table mapping key names to numeric values and shift classification. It supports build-time keymap tooling rather than runtime kernel behavior.

## Important APIs, Types, And Functions

`get_define()` reads `#define` lines from the current `infile`, extracts `def_name` and `def_val`, and updates global parser line count `lc`. `main()` seeds shift keys, opens `include/linux/input.h`, `include/uapi/linux/input-event-codes.h`, and `spk_priv_keyinfo.h`, adds matching symbols via helpers from `utils.h`, and prints `struct st_key_init init_key_data[]`.

## Control Flow

Environment variables `TOPDIR` and `SPKDIR` select source roots. For each input file, the generator loops over `get_define()`, filters symbols, parses decimal, hex, or `KEY + offset` forms, inserts valid keys into a hash table, then walks all hash buckets and prints initializer rows followed by a sentinel.

## State And Persistence Behavior

The program uses process-local globals from `utils.h` such as `key_table`, `def_name`, `def_val`, and `infile`. It persists output only to stdout for the build to redirect. It does not modify source files itself.

## Dependencies And Integration Points

It depends on standard C library headers, `utils.h` generator helpers, and the kernel source tree layout. Its output is consumed by Speakup keymap generation code, not by the running kernel module.

## Risks

Parsing is intentionally simple and assumes one-line `#define` forms. Macro expressions outside plain numbers, hex values, or `name + number` are skipped. Generated ordering follows hash buckets, so consumers should not assume source order.

## Test Signals

Run with default and explicit `TOPDIR`/`SPKDIR`, verify known `KEY_*` and Speakup constants appear, check the final sentinel row, and test malformed or missing input files through `open_input()` error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/makemapdata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/selection.c -->
# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/selection.c

## Purpose

`selection.c` bridges Speakup review commands to the kernel console selection and paste facilities. It lets Speakup mark a rectangular/character region using review cursor coordinates and asynchronously set or paste the console selection on a tty.

## Important APIs, Types, And Functions

Global coordinates `spk_xs`, `spk_ys`, `spk_xe`, `spk_ye`, and `spk_sel_cons` are shared with `main.c`. Public functions are `speakup_set_selection()`, `speakup_cancel_selection()`, `speakup_paste_selection()`, and `speakup_cancel_paste()`. `struct speakup_selection_work` packages a `work_struct`, `tiocl_selection`, and referenced `tty_struct`.

## Control Flow

Set-selection takes a tty reference, atomically claims the work item with `cmpxchg`, fills 1-based coordinates, and schedules work. Worker code clears existing selection under `console_lock()` and calls `set_selection_kernel()`, unless the foreground console changed since marking. Paste follows the same single-work-item pattern and calls `paste_selection()`.

## State And Persistence Behavior

Selection and paste are transient asynchronous work items. The tty kref is held until worker completion or cancellation. The selected text is stored by the kernel console selection subsystem, not by this file.

## Dependencies And Integration Points

It depends on console selection APIs, tty references, workqueues, memory barriers, and foreground VT state. `main.c` calls it from cut/paste Speakup commands after maintaining mark coordinates.

## Risks

The code is race-sensitive: it uses `cmpxchg`, `xchg`, `rmb`, and `wmb` to protect one outstanding operation and avoid lost tty references. Foreground console changes can invalidate a mark. Callers must tolerate `-EBUSY` if previous work has not completed.

## Test Signals

Test mark/cut across same and changed foreground consoles, concurrent cut requests, cancellation during pending work, paste cancellation, tty kref balance, and expected `-EBUSY` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/selection.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/serialio.c -->
# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/serialio.c

## Purpose

`serialio.c` implements Speakup's legacy direct 8250-style serial port transport for hardware synthesizers. It configures classic `ttyS0`-`ttyS3` UART I/O ports, provides byte input/output callbacks for `struct spk_synth`, and optionally handles receive interrupts for synths that feed status/index bytes back.

## Important APIs, Types, And Functions

The exported `spk_serial_io_ops` supplies `synth_out`, `send_xchar`, `tiocmset`, `synth_in`, `synth_in_nowait`, `flush_buffer`, and `wait_for_xmitr`. Public helpers are `spk_serial_init()`, `spk_serial_synth_probe()`, `spk_stop_serial_interrupt()`, and `spk_serial_release()`. Static state includes `rs_table`, `serstate`, and timeout counters.

## Control Flow

Probe validates `synth->ser`, calls `spk_serial_init()`, configures baud/divisor/LCR/MCR, requests the I/O region, checks for absent UART via `UART_LSR == 0xff`, starts interrupts when `read_buff_add` exists, sends a null and carriage return, and marks the synth alive. Output waits for THRE/TEMT and CTS, writes bytes, and deactivates the synth after repeated timeouts.

## State And Persistence Behavior

It owns the selected UART I/O region and IRQ while active, writes the selected base port to `speakup_info.port_tts`, and increments `timeouts` across writes. State is released on synth removal.

## Dependencies And Integration Points

It depends on serial register definitions, architecture `SERIAL_PORT_DFNS`, ioport reservation helpers from synth code, Speakup global locking, and per-synth `read_buff_add` callbacks. Serial synthesizer modules bind this transport through `io_ops = &spk_serial_io_ops`.

## Risks

This is low-level port I/O that can conflict with the normal serial driver; it even attempts to release and reclaim existing regions. Busy-wait loops and hardware flow-control assumptions can stall speech or deactivate Speakup on marginal hardware.

## Test Signals

Probe valid and invalid `ser` values, unavailable I/O regions, absent UART detection, CTS timeout handling, repeated timeout deactivation, IRQ receive buffering for DECtalk-style devices, and release path interrupt/region cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/serialio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/serialio.h -->
# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/serialio.h

## Purpose

`serialio.h` declares legacy serial-port support structures, timeout constants, tty index bounds, and UART helper macros used by `serialio.c` and serial-only synthesizer drivers.

## Important APIs, Types, And Functions

`struct old_serial_port` mirrors the minimal data needed from old 8250 serial tables: baud base, port, irq, and flags. Constants define serial, transmitter, CTS, and buffer timeouts; allowed tty indices; and timeout disable count. `spk_serial_tx_busy()` reads `UART_LSR` from `speakup_info.port_tts`.

## Control Flow

The header has no runtime control flow. It shapes how `serialio.c` waits for UART transmit readiness and validates `ser` module parameters.

## State And Persistence Behavior

It stores no state directly. Its macros read global Speakup serial state maintained by `serialio.c`.

## Dependencies And Integration Points

It includes Linux serial headers, `serial_core`, and `spk_priv.h`. Serial synthesizer drivers include it when they need direct I/O constants or custom probing.

## Risks

The comments identify this as copied legacy 8250 knowledge and "broken driver" territory. Macros assume `speakup_info.port_tts` is valid and point at a UART-like device.

## Test Signals

Compile coverage with architectures that define or omit `SERIAL_PORT_DFNS`, and runtime checks that timeout constants and `SPK_LO_TTY`/`SPK_HI_TTY` align with probe behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/serialio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup.h -->
# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup.h

## Purpose

`speakup.h` is the public internal header for the Speakup subsystem. It defines version/keymap constants, character classification bits, helper macros, subsystem function prototypes, and extern declarations for shared globals.

## Important APIs, Types, And Functions

Key constants include `SPEAKUP_VERSION`, `KEY_MAP_VER`, `SHIFT_TBL_SIZE`, `MAX_DESC_LEN`, `MAXVARLEN`, and chartab bit flags such as `SYNTH_OK`, `B_ALPHA`, `PUNC`, `WDLM`, `B_CTL`, and `B_SYM`. Prototypes cover thread, synth lifecycle, sysfs kobjects, variable handling, buffer writes, selection, devsynth, UTF-8 synth writes, and fake keyboard integration.

## Control Flow

The header does not execute code, but it defines cross-file call contracts: core code calls synth/buffer helpers, sysfs calls variable handlers, synth drivers call shared synth I/O helpers, and selection/devsynth expose user interaction surfaces.

## State And Persistence Behavior

Extern globals declared here are the in-memory shared state for Speakup: selected synth, console states, keymaps, punctuation masks, character descriptions, chartab, boot settings, and unprocessed beep state.

## Dependencies And Integration Points

It includes `spk_types.h` and `i18n.h`, binding all major Speakup compilation units to common types and message indexes.

## Risks

Because this header exposes many mutable globals, changes to variable IDs, character-class bits, or prototypes have broad blast radius. `KEY_MAP_VER` must stay synchronized with generated `speakupmap.h` data and sysfs keymap validation.

## Test Signals

Build all Speakup modules after header changes, verify keymap version compatibility, and exercise sysfs, keyboard, synth, and selection paths that consume the declared globals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_acnt.h -->
# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_acnt.h

## Purpose

`speakup_acnt.h` contains shared constants for Accent synthesizer drivers. It centralizes the driver version and device-specific control bytes.

## Important APIs, Types, And Functions

The header defines `DRV_VERSION`, `SYNTH_CLEAR`, and `PROCSPEECH`. It declares no functions or structs.

## Control Flow

There is no executable flow. `speakup_acntpc.c` and `speakup_acntsa.c` include it to populate their `struct spk_synth` descriptors and output logic.

## State And Persistence Behavior

It stores no state. The constants affect runtime synth flushing and process-speech commands in consuming drivers.

## Dependencies And Integration Points

It is guarded by `_SPEAKUP_ACNT_H` and has no includes, making it a small shared device contract.

## Risks

Changing constants affects both Accent PC and Accent SA behavior. Incorrect clear or process-speech bytes can leave hardware speaking stale buffered text or failing to flush.

## Test Signals

Build both Accent drivers and verify flush/process-speech behavior on each supported device path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_acnt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_acntpc.c -->
# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_acntpc.c

## Purpose

`speakup_acntpc.c` supports the internal Accent PC synthesizer. It uses direct I/O port access through `spk_serial_io_ops`, custom port probing, and custom output pacing.

## Important APIs, Types, And Functions

The driver registers `synth_acntpc` with name `acntpc`, `long_name` "Accent PC", Accent init string, and variables for caps strings, rate, pitch, volume, tone, and direct mode. Static functions include `synth_probe()`, `accent_release()`, `synth_immediate()`, `do_catch_up()`, and `synth_flush()`. Module params expose `port`, `start`, `rate`, `pitch`, `vol`, `tone`, and `direct`.

## Control Flow

Probe either uses forced `port` or scans `0x2a8`, requests the I/O range, checks for Accent-specific status, and marks the synth alive. Catch-up drains the shared synth buffer, waits for ready/full conditions, converts newline to `PROCSPEECH`, sends bytes, and periodically triggers speech after spaces or punctuation. Flush emits the Accent clear byte and releases the region on removal.

## State And Persistence Behavior

Driver state is the selected I/O port, forced-port flag, synth liveness, and registered sysfs variables. Settings are in memory and seeded from module params.

## Dependencies And Integration Points

It depends on `speakup_acnt.h`, `spk_priv.h`, `serialio.h`, the synth buffer API, variable registration through `synth_add()`, and sysfs attributes using `spk_var_show/store`.

## Risks

Direct port probing can conflict with other hardware. Timeout loops and full/ready interpretation are device-specific; wrong port selection can produce false positives or I/O stalls.

## Test Signals

Test forced and probed ports, region conflict handling, sysfs variable updates, immediate output backpressure, catch-up pacing, newline conversion, and release cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_acntpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_acntsa.c -->
# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_acntsa.c

## Purpose

`speakup_acntsa.c` supports the Accent SA serial/tty synthesizer. Unlike Accent PC, it uses the generic Speakup tty line discipline transport.

## Important APIs, Types, And Functions

It defines `synth_acntsa` with name `acntsa`, init string, timing values, `io_ops = &spk_ttyio_ops`, `probe = synth_probe`, `release = spk_ttyio_release`, and generic catch-up/flush helpers. Variables cover caps strings, rate, pitch, volume, tone, direct, and shared timing attributes. Module params include `ser`, `dev`, `start`, and voice parameters.

## Control Flow

Probe delegates to `spk_ttyio_synth_probe()` and logs device/version on success. Once selected, generic synth code sends formatted variable updates and buffered text through ttyio.

## State And Persistence Behavior

State is held in `synth_acntsa`, tty device pointer assigned by ttyio, liveness flag, and variable values. Runtime sysfs changes persist only while loaded.

## Dependencies And Integration Points

It depends on `speakup_acnt.h`, ttyio operations, shared catch-up and flush functions, and the `module_spk_synth()` registration macro.

## Risks

Most risk is in tty setup: invalid `ser`/`dev`, inability to set `N_SPEAKUP`, or missing hardware flow control. Device-specific risks are limited to command strings and range definitions.

## Test Signals

Probe with `dev` and `ser`, verify sysfs attributes under `/sys/accessibility/speakup/acntsa`, test variable formatting, tty disconnect/release, and restart after liveness failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_acntsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_apollo.c -->
# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_apollo.c

## Purpose

`speakup_apollo.c` supports Apollo II synthesizers over the Speakup tty line discipline. It provides Apollo-specific command strings, variable ranges, and a custom catch-up loop.

## Important APIs, Types, And Functions

`synth_apollo` registers name `apollo`, init string `@R3@D0@K1\r`, `spk_ttyio_ops`, generic tty probe/release/immediate output, and custom `do_catch_up()`. Variables include caps strings, language, rate, pitch, voice, volume, direct, and timing attributes. Module params expose `ser`, `dev`, `start`, `rate`, `pitch`, `vol`, `voice`, `lang`, and `direct`.

## Control Flow

TTY probe opens the selected device and installs `N_SPEAKUP`. The custom catch-up loop pulls Speakup buffer bytes, handles newline/process-speech conversion, observes synth fullness through output return values, and sleeps based on configured delay/jiffy values.

## State And Persistence Behavior

State resides in the synth descriptor, tty pointer, alive flag, and sysfs variable values. No persistent storage is used.

## Dependencies And Integration Points

The driver integrates with ttyio, shared synth buffer/thread code, `spk_var_show/store`, and `synth_add()`/`synth_remove()` through `module_spk_synth()`.

## Risks

Apollo command syntax differs from other serial synths; incorrect variable format strings can produce invalid device commands. TTY write-room failures deactivate speech through ttyio.

## Test Signals

Validate tty probe, Apollo init and variable command emission, language/voice sysfs handling, catch-up under full output, and clean release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_apollo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_audptr.c -->
# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_audptr.c

## Purpose

`speakup_audptr.c` supports the Audapter synthesizer through ttyio with Audapter-specific initialization, punctuation, and flush/version handling.

## Important APIs, Types, And Functions

`synth_audptr` registers name `audptr`, long name "Audapter", init bytes, `spk_ttyio_ops`, custom `synth_probe()`, custom `synth_flush()`, and generic catch-up. It defines variables for caps strings, pitch, punctuation, rate, tone, volume, direct, and timing. `synth_version()` queries/logs version data during probe.

## Control Flow

Probe initializes the tty line discipline and may query version information. Normal output uses shared catch-up through ttyio. Flush sends Audapter-specific clear/control sequences.

## State And Persistence Behavior

Runtime state is the tty attachment, alive flag, and variable values. Module params seed defaults and sysfs changes last until unload.

## Dependencies And Integration Points

It depends on ttyio transport, shared variable sysfs handlers, synth buffer helpers, and `module_spk_synth()`.

## Risks

The version/flush protocol expects specific device responses; timeouts or unexpected bytes can make probe noisy or leave stale speech. As with other tty synths, bad `dev` or line discipline failure prevents operation.

## Test Signals

Test probe/version query on available and unavailable devices, flush behavior, punctuation sysfs commands, direct mode, and tty release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_audptr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_bns.c -->
# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_bns.c

## Purpose

`speakup_bns.c` supports Braille 'N Speak synthesizers using the generic ttyio transport and mostly generic Speakup catch-up/flush behavior.

## Important APIs, Types, And Functions

`synth_bns` sets name `bns`, long name "Braille 'N Speak", init bytes, `spk_ttyio_ops`, generic tty probe/release/immediate, `spk_do_catch_up`, and `spk_synth_flush`. Variables expose caps strings, rate, pitch, volume, tone, direct, and timing attributes.

## Control Flow

Module registration adds the synth to the Speakup synthesizer list. Probe opens the selected tty and installs the line discipline. Output and flushing are handled by generic synth/tty paths.

## State And Persistence Behavior

Only in-memory synth descriptor, tty pointer, alive flag, and variable values are maintained. Module params seed runtime defaults.

## Dependencies And Integration Points

It integrates with ttyio, sysfs variable handlers, and the shared synth thread/buffer.

## Risks

The driver has little custom code, so main risks are device command compatibility and tty configuration. It cannot operate if `N_SPEAKUP` registration or selected tty open fails.

## Test Signals

Probe via `ser` and `dev`, inspect `/sys/accessibility/speakup/bns`, adjust rate/pitch/volume/tone, verify generic flush, and unload/reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_bns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_decext.c -->
# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_decext.c

## Purpose

`speakup_decext.c` supports DECtalk External synthesizers over ttyio. It implements DEC-specific speech command formatting, flow-control status from received bytes, punctuation-triggered speech, and escape-bracket tracking.

## Important APIs, Types, And Functions

`synth_decext` registers name `decext`, `SF_DEC`, DEC init string, `spk_ttyio_ops`, `read_buff_add()`, custom `do_catch_up()`, and custom `synth_flush()`. Variables include caps strings, rate, pitch, inflection, volume, punctuation, voice, direct, and timing.

## Control Flow

`read_buff_add()` stores the last received byte; `synth_full()` treats XOFF as full. Catch-up skips non-Latin-1, peeks buffer characters, waits while full, converts newline to carriage return, emits process-speech after punctuation/spacing, and avoids process-speech while inside DEC escape commands. Flush clears escape state, flushes tty buffer, and sends a DEC escape clear sequence immediately.

## State And Persistence Behavior

State includes volatile `last_char`, `in_escape`, synth variable values, tty attachment, and alive flag. No persistent storage exists.

## Dependencies And Integration Points

It relies on ttyio receive buffering, shared synth buffer APIs, jiffy/delay variables, and DEC flag handling in `main.c` punctuation spacing.

## Risks

Flow control is inferred from the last byte only, so missed XON/XOFF transitions can stall or overrun output. Escape-state mistakes can inject process-speech commands into DEC command strings.

## Test Signals

Test XON/XOFF handling, flush while in escape command, punctuation-triggered process speech, variable command ranges, and tty probe/release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_decext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_decpc.c -->
# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_decpc.c

## Purpose

`speakup_decpc.c` supports the internal DECtalk PC synthesizer board through a custom command/DMA-like I/O protocol over direct ports.

## Important APIs, Types, And Functions

The file defines many DECtalk PC status, command, control, DMA, and mode constants. `synth_dec_pc` registers name `decpc`, `SF_DEC`, `spk_serial_io_ops`, custom `synth_probe()`, `dtpc_release()`, `synth_immediate()`, `do_catch_up()`, and `synth_flush()`. Helpers include `dt_getstatus()`, `dt_sendcmd()`, `dt_waitbit()`, `dt_wait_dma()`, `dt_ctrl()`, `dt_sendchar()`, and `testkernel()`.

## Control Flow

Probe scans known base ports, reserves eight bytes, sends sync commands, verifies kernel/software readiness, and marks the synth alive. Catch-up waits for DMA readiness before sending each char, tracks DEC escape commands, emits process-speech after punctuation or jiffy intervals, and calls `synth_flush()` on Speakup flush requests. Flush uses DEC control commands, DMA sync, and status polling to clear hardware buffers.

## State And Persistence Behavior

Driver state includes `speakup_info.port_tts`, `dt_stat`, `dma_state`, `in_escape`, `is_flushing`, and variable values. I/O regions are reserved during operation and released on removal.

## Dependencies And Integration Points

It depends on low-level port I/O, the Speakup synth buffer/thread, variable sysfs handlers, and `module_spk_synth()`.

## Risks

The hardware protocol is complex and timing-sensitive. Failure to synchronize DMA state or detect flushing can drop characters or wedge speech. Port probing can conflict with other ISA devices.

## Test Signals

Test all probe ports, unavailable region handling, `testkernel()` failure codes, flush synchronization, `dt_sendchar()` backpressure, variable sysfs writes, and release cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_decpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_dectlk.c -->
# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_dectlk.c

## Purpose

`speakup_dectlk.c` supports DECtalk Express synthesizers over ttyio with DEC indexing support. It handles XON/XOFF, flush completion, voice-dependent default pitch/volume, and index feedback for read-all mode.

## Important APIs, Types, And Functions

`synth_dectlk` registers name `dectlk`, `SF_DEC`, ttyio transport, `read_buff_add()`, `get_index()`, custom catch-up/flush, `flush_time`, and indexing command `[:in re %d ]`. Variables cover caps, rate, pitch, inflection, volume, punctuation, voice, direct, and timing. `ap_defaults` and `g5_defaults` provide per-voice default pitch/volume.

## Control Flow

`read_buff_add()` processes DEC control bytes: control-A completes flush, XOFF/XON update `xoff`, digits accumulate index numbers, and printable bytes commit the last index. Catch-up waits for pending flush completion, drains the synth buffer with DEC escape tracking, emits process-speech safely, and inserts delays based on sysfs variables. Flush closes any open escape, marks `is_flushing`, flushes tty output, and sends the clear byte.

## State And Persistence Behavior

State includes `xoff`, `in_escape`, `is_flushing`, wait queue `flush`, `lastind`, per-voice defaults, tty state, and variable values. Index state is consumed and reset by `get_index()`.

## Dependencies And Integration Points

It integrates with read-all indexing in `main.c`, ttyio receive callbacks, generic variable store voice-default reset logic, and the synth buffer thread.

## Risks

Flush waits and index parsing depend on exact device feedback. Losing a control-A can delay catch-up until `flush_time` expires. Incorrect escape tracking can send process-speech inside DEC commands.

## Test Signals

Test XON/XOFF, flush completion timeout, read-all index insertion/feedback, voice changes resetting pitch/volume defaults, and sysfs `flush_time`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_dectlk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_dtlk.c -->
# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_dtlk.c

## Purpose

`speakup_dtlk.c` supports RC Systems DoubleTalk PC internal synthesizers using direct port I/O and DoubleTalk-specific status interrogation.

## Important APIs, Types, And Functions

`synth_dtlk` registers name `dtlk`, init bytes, `spk_serial_io_ops`, custom probe/release/immediate/catch-up/flush, and indexing through `spk_synth_get_index()`. Helpers include `synth_readable()`, `synth_writable()`, `synth_full()`, `spk_out()`, `synth_read_tts()`, and `synth_interrogate()`. Variables include caps, rate, pitch, volume, tone, punctuation, voice, frequency, and direct.

## Control Flow

Probe uses a forced port or scans known base ports, reserves the I/O extent, checks expected signature, waits for readiness, interrogates ROM/version/serial/settings, and marks alive. Catch-up waits while almost full, sends bytes with `spk_out()`, converts newline to `PROCSPEECH`, and periodically triggers speech after spaces. Immediate output returns the remaining buffer on full hardware.

## State And Persistence Behavior

State includes selected LPC/base port, `speakup_info.port_tts`, `synth_status`, alive flag, and variable values. The I/O extent is released on driver removal.

## Dependencies And Integration Points

It depends on `speakup_dtlk.h` hardware constants, `serialio.h`, synth buffer APIs, and generic synth registration.

## Risks

Busy waits for readable/writable status can spin if hardware misbehaves. Probe signature matching and direct I/O can collide with other ISA devices. Interrogation assumes a bounded valid response ending with `0x7f`.

## Test Signals

Test forced/probed ports, interrogation parsing, full/readable/writable status behavior, indexing command emission, flush, and release path region cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_dtlk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_dtlk.h -->
# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_dtlk.h

## Purpose

`speakup_dtlk.h` defines DoubleTalk PC hardware constants and the status structure returned by the device interrogation command.

## Important APIs, Types, And Functions

Constants include `SYNTH_IO_EXTENT`, `SYNTH_CLEAR`, `TTS_READABLE`, `TTS_SPEAKING`, `TTS_SPEAKING2`, `TTS_WRITABLE`, and `TTS_ALMOST_FULL`. `struct synth_settings` captures serial number, ROM version, mode, punctuation level, frequency, pitch, speed, volume, tone, expression, dictionary flags, free RAM, articulation, reverb, and end-of-block.

## Control Flow

No executable flow is present. `speakup_dtlk.c` uses the constants to interpret status bytes and parse interrogation responses.

## State And Persistence Behavior

The header stores no state. It defines the shape of local stack/static data in the driver.

## Dependencies And Integration Points

It is a private device-contract header included by the DoubleTalk driver only.

## Risks

Incorrect bit definitions cause the driver to misread readiness/fullness and can hang or drop output. Structure field ordering must match firmware response bytes.

## Test Signals

Verify `synth_interrogate()` output against known hardware, compile the driver, and test status-bit transitions for readable, writable, and almost-full paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_dtlk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_dummy.c -->
# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_dummy.c

## Purpose

`speakup_dummy.c` provides a dummy tty-backed synthesizer useful for testing the Speakup synth path without a real hardware-specific protocol.

## Important APIs, Types, And Functions

`synth_dummy` registers name `dummy`, init string `Speakup\n`, ttyio transport, `spk_do_catch_up_unicode`, generic flush, restart liveness check, and `read_buff_add()` for simple receive buffering. Variables include caps strings, rate, pitch, inflection, volume, tone, punctuation, direct, and timing.

## Control Flow

Probe delegates to ttyio. Output is Unicode-capable through generic catch-up and ttyio UTF-8 output support. Sysfs variables format commands like a software-ish synth protocol.

## State And Persistence Behavior

State is limited to tty attachment, alive flag, simple receive buffer behavior, and variable values. It is not persistent.

## Dependencies And Integration Points

It depends on ttyio, generic unicode catch-up, shared variable handlers, and `module_spk_synth()`.

## Risks

Because it is a dummy protocol, it may not reveal timing and hardware-flow bugs that real drivers encounter. It still depends on valid tty line discipline setup.

## Test Signals

Use it for smoke tests of synth selection, ttyio open/release, Unicode output, sysfs variable handling, and no-hardware Speakup operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_dummy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_keypc.c -->
# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_keypc.c

## Purpose

`speakup_keypc.c` supports Keynote Gold PC internal synthesizers through direct I/O port access and Keynote-specific pacing/control bytes.

## Important APIs, Types, And Functions

`synth_keypc` registers name `keypc`, init string, `spk_serial_io_ops`, custom probe/release/immediate/catch-up/flush, and variables for caps, rate, pitch, direct, and timing. Helpers include `synth_writable()`, `synth_full()`, and `oops()` timeout diagnostics.

## Control Flow

Probe uses a forced port or scans `0x2a8`, reserves a four-byte region, expects status `0x80`, and marks alive. Immediate and catch-up loops wait for not-full and writable transitions, convert newline to `PROCSPEECH`, emit bytes with `outb_p()`, and periodically send process-speech after spaces.

## State And Persistence Behavior

State includes selected `synth_port`, forced-port value, synth liveness, and variable values. The I/O region is released on `keynote_release()`.

## Dependencies And Integration Points

It depends on serial register definitions, `spk_priv.h`, synth buffer helpers, sysfs variable handlers, and `module_spk_synth()`.

## Risks

The `synth_writable()` loop semantics are device-specific and guarded by fixed timeouts. Bad hardware or wrong port can produce timeout warnings and lost speech. Direct I/O probing can conflict with other devices.

## Test Signals

Test port override, region conflict, absent hardware, timeout diagnostics, catch-up pacing, flush byte, and sysfs variable range enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_keypc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_ltlk.c -->
# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_ltlk.c

## Purpose

`speakup_ltlk.c` supports LiteTalk synthesizers over ttyio. It is closely related to DoubleTalk command formatting but uses the tty transport.

## Important APIs, Types, And Functions

`synth_ltlk` registers name `ltlk`, init bytes, `spk_ttyio_ops`, custom `synth_probe()`, generic tty release/immediate, generic catch-up/flush, restart liveness, and indexing via `spk_synth_get_index()`. Variables include caps, rate, pitch, volume, tone, punctuation, voice, frequency, direct, and timing.

## Control Flow

Probe initializes ttyio and may perform a lightweight synth-specific check. After registration, the shared synth thread formats variables and drains buffered speech through ttyio. Index commands support read-all behavior.

## State And Persistence Behavior

State is the synth descriptor, tty attachment, alive flag, indexing cursor in `struct spk_synth`, and runtime variables.

## Dependencies And Integration Points

It integrates with ttyio, shared synth indexing helpers, variable sysfs, and `module_spk_synth()`.

## Risks

Command strings and index behavior must match LiteTalk firmware. Generic tty failures remain the main operational risk.

## Test Signals

Test tty probe, index command emission/reading, variable command formatting, direct mode, and release/restart paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_ltlk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_soft.c -->
# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_soft.c

## Purpose

`speakup_soft.c` implements the software synthesizer backend. It exposes `/dev/softsynth` and `/dev/softsynthu` misc devices so user-space speech daemons can read Speakup's buffered output and write back spoken index numbers.

## Important APIs, Types, And Functions

`synth_soft` registers name `soft`, no `io_ops`, misc-device probe/release, `softsynth_is_alive()`, `softsynth_adjust()`, and `get_index()`. File operations include `softsynth_open()`, `softsynth_close()`, `softsynth_read()`, `softsynthu_read()`, `softsynth_write()`, and `softsynth_poll()`. `get_initstring()` emits current variable settings for a reader.

## Control Flow

Probe registers two misc devices. A reader opens one device, waits on `speakup_event` until this synth is current and buffer data or flush is available, receives init commands, flush byte, and buffered chars; `/dev/softsynthu` encodes Unicode as UTF-8 while `/dev/softsynth` skips non-Latin-1. Writes parse an index number for read-all feedback.

## State And Persistence Behavior

State includes `misc_registered`, `init_pos`, `synth_soft.alive`, and `last_index`. Output buffers are shared with core synth code. Device nodes are registered only while the module/synth is active.

## Dependencies And Integration Points

It depends on miscdevice, poll/wait queues, user-copy APIs, synth buffer helpers, `synth_current()`, and `main.c` read-all indexing.

## Risks

Reader semantics are blocking and lock-sensitive. User-copy failures can abort reads after state changes. Only one alive reader is allowed. Non-Unicode device drops non-Latin-1 output, which can surprise tests.

## Test Signals

Test misc registration/deregistration, exclusive open, blocking and nonblocking reads, poll readiness, flush byte delivery, UTF-8 encoding, index write parsing, close waking tty output, and punctuation-level adjustment propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_soft.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_spkout.c -->
# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_spkout.c

## Purpose

`speakup_spkout.c` supports Speak Out synthesizers over ttyio with a small set of device-specific command strings.

## Important APIs, Types, And Functions

`synth_spkout` registers name `spkout`, init bytes, `spk_ttyio_ops`, generic tty probe/release/immediate, generic catch-up, custom or shared flush, restart liveness, and indexing via `spk_synth_get_index()`. Variables include caps, pitch, punctuation, rate, tone, volume, direct, and timing.

## Control Flow

The driver is registered through `module_spk_synth()`. Probe is the ttyio path; output uses the common synth catch-up path. Flush sends the Speak Out clear command.

## State And Persistence Behavior

State is the synth descriptor, tty pointer, alive flag, indexing state, and variable values.

## Dependencies And Integration Points

It uses ttyio, shared variable sysfs handlers, synth buffer/index helpers, and the common registration lifecycle.

## Risks

The module params include `vol` wired to `vars[PITCH_ID].u.n.default_val`, which looks suspicious and should be treated as a test/review signal. Otherwise risk is mostly tty/device compatibility.

## Test Signals

Verify sysfs/module parameter mapping, especially `vol`, tty probe/release, indexing support, flush command, and variable formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_spkout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_txprt.c -->
# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_txprt.c

## Purpose

`speakup_txprt.c` supports Transport synthesizers over ttyio with generic Speakup output handling and Transport-specific variable command strings.

## Important APIs, Types, And Functions

`synth_txprt` registers name `txprt`, init byte sequence, `spk_ttyio_ops`, generic tty probe/release/immediate, `spk_do_catch_up`, `spk_synth_flush`, restart liveness, and variables for caps, rate, pitch, volume, tone, direct, and timing.

## Control Flow

After module registration, probe attaches to the selected tty. The generic synth thread drains buffered speech through ttyio using command formats from `vars`.

## State And Persistence Behavior

Runtime state is held in the synth descriptor, tty device pointer, alive flag, and variable values. No persistent storage is used.

## Dependencies And Integration Points

It depends on ttyio, shared synth/variable/sysfs infrastructure, and `module_spk_synth()`.

## Risks

This driver has minimal custom logic, so risk concentrates in tty setup and command compatibility with Transport devices.

## Test Signals

Probe with `ser`/`dev`, adjust all sysfs variables, test generic flush and catch-up, and verify module unload releases tty state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_txprt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/spk_priv.h -->
# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/spk_priv.h

## Purpose

`spk_priv.h` is Speakup's private cross-file header. It defines internal constants, synth registration helpers, transport prototypes, synth buffer functions, variable sysfs callbacks, and shared globals.

## Important APIs, Types, And Functions

Constants include `SYNTH_CHECK`, `SYNTH_START`, `KT_SPKUP`, default synth device/serial settings, and `SPK_SYNTH_TIMEOUT`. Prototypes cover serial/tty transport, synth buffer reads, variable lookup/show/store, synth probe/immediate/catch-up/flush/liveness helpers, formatted synth output, region reservation, `synth_add/remove/current`, and exported `spk_serial_io_ops`/`spk_ttyio_ops`.

## Control Flow

It has no executable flow, but `module_spk_synth()` users depend on its `synth_add()`/`synth_remove()` contract. Core and driver files call through these prototypes to share the synth buffer and variable systems.

## State And Persistence Behavior

It declares `speakup_info` and `synth_time_vars`, both process-global kernel state. Other state is declared in `speakup.h`.

## Dependencies And Integration Points

It includes `spk_types.h` and `spk_priv_keyinfo.h`, making it the common private include for most Speakup implementation files.

## Risks

Prototype or constant changes can silently break all synth drivers. `SYNTH_CHECK` validates synth module compatibility and must match `struct spk_synth.checkval` expectations.

## Test Signals

Full Speakup build coverage, module load for several synth drivers, and sysfs variable read/write tests after header changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/spk_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/spk_priv_keyinfo.h -->
# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/spk_priv_keyinfo.h

## Purpose

`spk_priv_keyinfo.h` defines Speakup private key action IDs used by generated keymaps and keyboard dispatch. It names review commands, edit modes, variable increment/decrement commands, and key ranges.

## Important APIs, Types, And Functions

The header declares numeric constants such as `SPK_KEY`, `SPEAKUP_GOTO`, `SPEECH_KILL`, review commands, window commands, help/lock/cursor/read-all actions, edit-bit actions, `SPKUP_MAX_FUNC`, and variable command range markers like `VAR_START` and `FIRST_SET_VAR`.

## Control Flow

It does not execute code. `main.c` relies on the values to index `spkup_handler[]`, decide whether a key invokes a function or variable adjustment, and validate special handler input. `makemapdata.c` parses the defines for build-time key-name generation.

## State And Persistence Behavior

No state is stored. Numeric stability matters because keymap data refers to these IDs.

## Dependencies And Integration Points

It is included by `spk_priv.h` and read by the keymap generator. Values must remain coordinated with handler ordering in `main.c` and generated `speakupmap.h`.

## Risks

Renumbering or inserting constants in the wrong place can dispatch keys to incorrect handlers or variable IDs. Handler array comments explicitly require ordering to match these definitions.

## Test Signals

Regenerate keymap data, load default keymap, exercise every Speakup command, and verify variable inc/dec key IDs map to the intended `var_id_t`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/spk_priv_keyinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/spk_ttyio.c -->
# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/spk_ttyio.c

## Purpose

`spk_ttyio.c` implements Speakup's modern tty line discipline transport. It lets synth drivers use normal tty devices such as `ttyS0` or `ttyUSB0` instead of stealing UART I/O ports directly.

## Important APIs, Types, And Functions

`struct spk_ldisc_data` stores one received byte, a completion, buffer-free flag, and synth pointer. Exported APIs are `spk_ttyio_ops`, `spk_ttyio_register_ldisc()`, `spk_ttyio_unregister_ldisc()`, `spk_ttyio_synth_probe()`, `spk_ttyio_release()`, and `spk_ttyio_synth_immediate()`. Static helpers handle `ser` to device conversion, tty open/close, `N_SPEAKUP` line discipline open/receive callbacks, output, UTF-8 encoding, modem control, input waits, and flush.

## Control Flow

Probe resolves `synth->dev_name` or `synth->ser`, opens the tty exclusively, enables hardware flow control when possible, temporarily sets `speakup_tty` so only Speakup can install `N_SPEAKUP`, attaches the line discipline, stores the tty in `synth->dev`, and marks alive. Receive callbacks either pass all bytes to `synth->read_buff_add()` or complete a one-byte wait for polling input. Output writes through `tty->ops->write`.

## State And Persistence Behavior

State includes global `speakup_tty` protected by `speakup_tty_mutex`, per-tty `disc_data`, and `synth->dev`. The line discipline is registered at Speakup init and removed at exit.

## Dependencies And Integration Points

It depends on tty core, line discipline registration, completions, termios, Speakup synth descriptors, and generic synth drivers using `spk_ttyio_ops`.

## Risks

TTY lifetime and line discipline ownership are delicate. Failed opens must close/kclose correctly. The single-byte receive path uses memory barriers and can drop bytes when the consumer has not freed the buffer. Write errors deactivate the synth and restart stopped ttys.

## Test Signals

Test ldisc registration failure, invalid `ser`, `dev` lookup, exclusive open failure, flow-control setting, unauthorized ldisc open, read callbacks with and without `read_buff_add`, Unicode output, write error deactivation, and release cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/spk_ttyio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/spk_types.h -->
# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/spk_types.h

## Purpose

`spk_types.h` defines the central data model for Speakup: variable IDs/types, per-console state, synth I/O operations, synth descriptors, highlighting state, and shared subsystem metadata.

## Important APIs, Types, And Functions

Enums include `var_type_t`, numeric operation modes `E_DEFAULT`/`E_SET`/`E_INC`/`E_DEC`/`E_NEW_DEFAULT`, and `var_id_t` from `VERSION` through `MAXVARS`. Important structs include `spk_highlight_color_track`, `st_spk_t`, `st_var_header`, `num_var_t`, `punc_var_t`, `string_var_t`, `var_t`, `st_bits_data`, `synth_indexing`, `spk_io_ops`, `spk_synth`, and `speakup_info_t`. Macros map concise names like `spk_x` and `win_top` to current console state.

## Control Flow

No code executes here, but the function pointers in `spk_io_ops` and `spk_synth` define all synth driver callbacks: output, input, flush, probe, release, immediate output, catch-up, liveness, adjustment, receive buffer, and indexing.

## State And Persistence Behavior

The structs define in-memory state held by `main.c`, synth drivers, and variable handlers. `spk_synth.attributes` maps drivers into sysfs attribute groups; `spk_synth.dev` stores transport-specific device state.

## Dependencies And Integration Points

It includes core kernel headers for types, fs, wait queues, modules, VT, locks, I/O, and devices. Almost every Speakup source includes it directly or through private/public headers.

## Risks

`var_id_t` ordering is explicitly ABI-like because `speakupmap.h` depends on values starting at `SPELL_DELAY`. Changing struct layouts or enum ordering affects all drivers, sysfs variable handling, and keymap dispatch.

## Test Signals

After type changes, rebuild all Speakup objects, load multiple hardware and software synth modules, verify sysfs attributes, keymap variable inc/dec, read-all indexing, and per-console cursor/window state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/spk_types.h -->
