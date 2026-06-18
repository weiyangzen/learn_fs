# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/Kconfig Research

## Purpose
This Kconfig file defines the Speakup console speech screen reader and its supported synthesizer drivers. It presents `SPEAKUP` as a tristate core and then exposes hardware, software, and dummy synthesizer options under that core.

## Important Options And Control Flow
`CONFIG_SPEAKUP` depends on `VT` and may be built in or as a module. `CONFIG_SPEAKUP_SERIALIO` defaults to `y` when ISA or compile-test plus I/O port support are present. Individual synthesizer options cover Accent, Apollo, Audapter, Braille 'n Speak, DECtalk variants, DoubleTalk, Keynote, LiteTalk, software synth, Speakout, Transport, and Dummy. Several internal-card options depend on `SPEAKUP_SERIALIO`; `SPEAKUP_SYNTH_DECPC` also depends on `m`, forcing module-only construction.

## State And Persistence
Persistent state is the generated `.config` selection of the core and synthesizer symbols. Runtime state is owned by Speakup implementation files.

## Dependencies And Integration Points
This file integrates with `drivers/accessibility/Kconfig`, `drivers/accessibility/speakup/Makefile`, VT support, ISA and I/O-port availability, and module build constraints. The help text documents early-boot screen reader support and the external DECtalk PC preload requirement.

## Risks
Incorrect dependency changes can make unsupported ISA or I/O-port drivers selectable. Since Speakup can be built in for early boot accessibility, dependency mistakes may break a boot-critical access path. The `depends on m` DECtalk PC constraint is intentional because the card requires userspace-loaded software before module load.

## Test Signals
Run Kconfig matrix checks for `SPEAKUP=y`, `m`, and `n`; with and without `HAS_IOPORT`; with `COMPILE_TEST`; and for the module-only DECtalk PC option. Build tests should confirm each selected synthesizer maps to an object.
