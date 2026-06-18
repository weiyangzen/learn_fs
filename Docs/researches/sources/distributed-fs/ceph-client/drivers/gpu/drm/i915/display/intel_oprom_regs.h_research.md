# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_oprom_regs.h

Purpose: defines MMIO registers and bit masks for option ROM/SPI region access.

Important definitions: `PRIMARY_SPI_TRIGGER`, `PRIMARY_SPI_ADDRESS`, `PRIMARY_SPI_REGIONID`, `SPI_STATIC_REGIONS`, `OPTIONROM_SPI_REGIONID_MASK`, `OROM_OFFSET`, and `OROM_OFFSET_MASK`.

Control flow/state: no executable logic. The macros describe register offsets and fields used by option ROM discovery or reads elsewhere in the display/GPU code.

Dependencies/integration: depends on MMIO and register field helper macros from the display register infrastructure, though this tiny header itself only lists definitions.

Risks/test signals: the risk is incorrect register address or field mask, which would break option ROM access. Build coverage and hardware tests that read VBIOS/option ROM data are the relevant signals.
