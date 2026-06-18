# sources/distributed-fs/ceph-client/sound/soc/fsl/eukrea-tlv320.c

## Purpose
`eukrea-tlv320.c` is an ASoC machine driver for Eukrea CPUIMX boards using an i.MX SSI interface connected to a TLV320AIC23 codec in I2S mode. It supports both device-tree probing and legacy machine-ID based configuration, including AUDMUX routing setup for older i.MX variants.

## Important APIs, Types, And Functions
The main card is `eukrea_tlv320` with one DAI link `eukrea_tlv320_dai`. `eukrea_tlv320_hw_params()` configures codec sysclk, CPU TDM slot mask, and CPU SSI clocking. `eukrea_tlv320_probe()` parses DT or legacy component names, configures AUDMUX through `imx_audmux_v1_configure_port()` or `imx_audmux_v2_configure_port()`, and registers the card. The platform driver matches `eukrea,asoc-tlv320` and has alias `platform:eukrea_tlv320`.

## Control Flow
On probe, the driver attaches the card to the platform device. With DT, it parses `eukrea,model`, resolves `ssi-controller`, follows the SSI `codec-handle`, reads `fsl,mux-int-port` and `fsl,mux-ext-port`, converts one-based DT port numbers to zero-based AUDMUX API values, and assigns CPU/platform/codec OF nodes. Without DT, it hard-codes `imx-ssi.0`, `tlv320aic23-codec.0-001a`, and card name `cpuimx-audio`. It then selects AUDMUX v1 routing for i.MX27 or `fsl,imx21-audmux`, AUDMUX v2 routing for i.MX25/35/51 or `fsl,imx31-audmux`, or exits successfully on unrelated legacy machines. Finally it registers the card. During stream setup, `hw_params()` sets the TLV320 clock to 12 MHz output, programs stereo SSI TDM slots, and tolerates `-EINVAL` from CPU `set_sysclk()` because `fsl_ssi` lacks that op.

## State And Persistence
Card and DAI link structures are static and mutated during probe with OF nodes or legacy component names. AUDMUX routing persists in SoC mux registers after configuration. There is no explicit remove path; devm card registration handles cleanup for bound devices.

## Dependencies And Integration Points
The driver depends on ASoC card/link APIs, TLV320AIC23 codec DAI, i.MX SSI, i.MX AUDMUX v1/v2 helpers, DT phandles/properties, legacy machine macros, I2C codec presence, and clocking assumptions around a 12 MHz codec clock. Kconfig selects TLV320 I2C, AUDMUX, FSL SSI, and i.MX PCM DMA.

## Risks And Edge Cases
Static global DAI/card mutation limits multi-instance safety. DT parsing returns errors for missing model, SSI, or mux properties, but a missing codec handle only logs an error and continues with a NULL codec OF node. The `tmp_np` assignment inside conditionals must be balanced with `of_node_put()`, which the code does in each matching branch. Legacy no-DT probing returns success on unrelated machines to avoid failing module load. CPU `set_tdm_slot()` return is ignored.

## Test Signals
Test DT success and each missing-property failure, codec-handle absence behavior, one-based to zero-based AUDMUX conversion, AUDMUX v1 and v2 register calls, legacy CPUIMX27/25/35/51 paths, unrelated legacy machine no-op success, `hw_params()` codec sysclk failure, tolerated CPU `set_sysclk()` `-EINVAL`, card registration failure logging, and module alias/OF match binding.
