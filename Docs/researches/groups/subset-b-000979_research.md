# subset-b-000979 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_cout0_master_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_cout0_master_regs.h

Purpose: Auto-generated Gaudi2 DCORE0 MME low-control AGU register map for the COUT0 master address-generation core. It exposes five ROI base-offset MMIO addresses for the `MME_AGU_CORE` prototype at 0x40CB22C-0x40CB23C.

Important APIs/types/functions: There are no C functions or types. The exported API is the macro family `mmDCORE0_MME_CTRL_LO_ARCH_AGU_COUT0_MASTER_ROI_BASE_OFFSET_0` (0x40CB22C), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_COUT0_MASTER_ROI_BASE_OFFSET_1` (0x40CB230), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_COUT0_MASTER_ROI_BASE_OFFSET_2` (0x40CB234), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_COUT0_MASTER_ROI_BASE_OFFSET_3` (0x40CB238), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_COUT0_MASTER_ROI_BASE_OFFSET_4` (0x40CB23C), one register per ROI base-offset slot 0 through 4.

Control flow: No executable control flow exists in this header. Runtime flow is created by MME descriptor programming code that writes these offsets while configuring tensor or output regions before launching MME work.

State and persistence behavior: The file stores no runtime state; the macros name persistent hardware registers in DCORE0. Values written to these registers live in the device until reset or later driver/firmware programming overwrites them.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. These AGU offsets pair with the tensor/base-address descriptor headers in the same `dcore0_mme_ctrl_lo_arch_*` block.

Risks: The master/slave and input/output variants are adjacent and easy to confuse; writing the wrong ROI offset can redirect tensor reads or COUT writes. Because the file is generated, manual edits would drift from the hardware database.

Test signals: Build coverage catches missing macro names. Hardware or simulator tests should program MME descriptors using this COUT0 master lane, verify expected tensor addressing, and compare register dumps against the 0x40CB22C-0x40CB23C address window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_cout0_master_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_cout0_slave_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_cout0_slave_regs.h

Purpose: Auto-generated Gaudi2 DCORE0 MME low-control AGU register map for the COUT0 slave address-generation core. It exposes five ROI base-offset MMIO addresses for the `MME_AGU_CORE` prototype at 0x40CB240-0x40CB250.

Important APIs/types/functions: There are no C functions or types. The exported API is the macro family `mmDCORE0_MME_CTRL_LO_ARCH_AGU_COUT0_SLAVE_ROI_BASE_OFFSET_0` (0x40CB240), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_COUT0_SLAVE_ROI_BASE_OFFSET_1` (0x40CB244), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_COUT0_SLAVE_ROI_BASE_OFFSET_2` (0x40CB248), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_COUT0_SLAVE_ROI_BASE_OFFSET_3` (0x40CB24C), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_COUT0_SLAVE_ROI_BASE_OFFSET_4` (0x40CB250), one register per ROI base-offset slot 0 through 4.

Control flow: No executable control flow exists in this header. Runtime flow is created by MME descriptor programming code that writes these offsets while configuring tensor or output regions before launching MME work.

State and persistence behavior: The file stores no runtime state; the macros name persistent hardware registers in DCORE0. Values written to these registers live in the device until reset or later driver/firmware programming overwrites them.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. These AGU offsets pair with the tensor/base-address descriptor headers in the same `dcore0_mme_ctrl_lo_arch_*` block.

Risks: The master/slave and input/output variants are adjacent and easy to confuse; writing the wrong ROI offset can redirect tensor reads or COUT writes. Because the file is generated, manual edits would drift from the hardware database.

Test signals: Build coverage catches missing macro names. Hardware or simulator tests should program MME descriptors using this COUT0 slave lane, verify expected tensor addressing, and compare register dumps against the 0x40CB240-0x40CB250 address window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_cout0_slave_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_cout1_master_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_cout1_master_regs.h

Purpose: Auto-generated Gaudi2 DCORE0 MME low-control AGU register map for the COUT1 master address-generation core. It exposes five ROI base-offset MMIO addresses for the `MME_AGU_CORE` prototype at 0x40CB254-0x40CB264.

Important APIs/types/functions: There are no C functions or types. The exported API is the macro family `mmDCORE0_MME_CTRL_LO_ARCH_AGU_COUT1_MASTER_ROI_BASE_OFFSET_0` (0x40CB254), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_COUT1_MASTER_ROI_BASE_OFFSET_1` (0x40CB258), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_COUT1_MASTER_ROI_BASE_OFFSET_2` (0x40CB25C), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_COUT1_MASTER_ROI_BASE_OFFSET_3` (0x40CB260), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_COUT1_MASTER_ROI_BASE_OFFSET_4` (0x40CB264), one register per ROI base-offset slot 0 through 4.

Control flow: No executable control flow exists in this header. Runtime flow is created by MME descriptor programming code that writes these offsets while configuring tensor or output regions before launching MME work.

State and persistence behavior: The file stores no runtime state; the macros name persistent hardware registers in DCORE0. Values written to these registers live in the device until reset or later driver/firmware programming overwrites them.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. These AGU offsets pair with the tensor/base-address descriptor headers in the same `dcore0_mme_ctrl_lo_arch_*` block.

Risks: The master/slave and input/output variants are adjacent and easy to confuse; writing the wrong ROI offset can redirect tensor reads or COUT writes. Because the file is generated, manual edits would drift from the hardware database.

Test signals: Build coverage catches missing macro names. Hardware or simulator tests should program MME descriptors using this COUT1 master lane, verify expected tensor addressing, and compare register dumps against the 0x40CB254-0x40CB264 address window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_cout1_master_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_cout1_slave_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_cout1_slave_regs.h

Purpose: Auto-generated Gaudi2 DCORE0 MME low-control AGU register map for the COUT1 slave address-generation core. It exposes five ROI base-offset MMIO addresses for the `MME_AGU_CORE` prototype at 0x40CB268-0x40CB278.

Important APIs/types/functions: There are no C functions or types. The exported API is the macro family `mmDCORE0_MME_CTRL_LO_ARCH_AGU_COUT1_SLAVE_ROI_BASE_OFFSET_0` (0x40CB268), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_COUT1_SLAVE_ROI_BASE_OFFSET_1` (0x40CB26C), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_COUT1_SLAVE_ROI_BASE_OFFSET_2` (0x40CB270), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_COUT1_SLAVE_ROI_BASE_OFFSET_3` (0x40CB274), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_COUT1_SLAVE_ROI_BASE_OFFSET_4` (0x40CB278), one register per ROI base-offset slot 0 through 4.

Control flow: No executable control flow exists in this header. Runtime flow is created by MME descriptor programming code that writes these offsets while configuring tensor or output regions before launching MME work.

State and persistence behavior: The file stores no runtime state; the macros name persistent hardware registers in DCORE0. Values written to these registers live in the device until reset or later driver/firmware programming overwrites them.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. These AGU offsets pair with the tensor/base-address descriptor headers in the same `dcore0_mme_ctrl_lo_arch_*` block.

Risks: The master/slave and input/output variants are adjacent and easy to confuse; writing the wrong ROI offset can redirect tensor reads or COUT writes. Because the file is generated, manual edits would drift from the hardware database.

Test signals: Build coverage catches missing macro names. Hardware or simulator tests should program MME descriptors using this COUT1 slave lane, verify expected tensor addressing, and compare register dumps against the 0x40CB268-0x40CB278 address window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_cout1_slave_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_in0_master_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_in0_master_regs.h

Purpose: Auto-generated Gaudi2 DCORE0 MME low-control AGU register map for the IN0 master address-generation core. It exposes five ROI base-offset MMIO addresses for the `MME_AGU_CORE` prototype at 0x40CB15C-0x40CB16C.

Important APIs/types/functions: There are no C functions or types. The exported API is the macro family `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN0_MASTER_ROI_BASE_OFFSET_0` (0x40CB15C), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN0_MASTER_ROI_BASE_OFFSET_1` (0x40CB160), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN0_MASTER_ROI_BASE_OFFSET_2` (0x40CB164), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN0_MASTER_ROI_BASE_OFFSET_3` (0x40CB168), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN0_MASTER_ROI_BASE_OFFSET_4` (0x40CB16C), one register per ROI base-offset slot 0 through 4.

Control flow: No executable control flow exists in this header. Runtime flow is created by MME descriptor programming code that writes these offsets while configuring tensor or output regions before launching MME work.

State and persistence behavior: The file stores no runtime state; the macros name persistent hardware registers in DCORE0. Values written to these registers live in the device until reset or later driver/firmware programming overwrites them.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. These AGU offsets pair with the tensor/base-address descriptor headers in the same `dcore0_mme_ctrl_lo_arch_*` block.

Risks: The master/slave and input/output variants are adjacent and easy to confuse; writing the wrong ROI offset can redirect tensor reads or COUT writes. Because the file is generated, manual edits would drift from the hardware database.

Test signals: Build coverage catches missing macro names. Hardware or simulator tests should program MME descriptors using this IN0 master lane, verify expected tensor addressing, and compare register dumps against the 0x40CB15C-0x40CB16C address window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_in0_master_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_in0_slave_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_in0_slave_regs.h

Purpose: Auto-generated Gaudi2 DCORE0 MME low-control AGU register map for the IN0 slave address-generation core. It exposes five ROI base-offset MMIO addresses for the `MME_AGU_CORE` prototype at 0x40CB170-0x40CB180.

Important APIs/types/functions: There are no C functions or types. The exported API is the macro family `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN0_SLAVE_ROI_BASE_OFFSET_0` (0x40CB170), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN0_SLAVE_ROI_BASE_OFFSET_1` (0x40CB174), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN0_SLAVE_ROI_BASE_OFFSET_2` (0x40CB178), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN0_SLAVE_ROI_BASE_OFFSET_3` (0x40CB17C), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN0_SLAVE_ROI_BASE_OFFSET_4` (0x40CB180), one register per ROI base-offset slot 0 through 4.

Control flow: No executable control flow exists in this header. Runtime flow is created by MME descriptor programming code that writes these offsets while configuring tensor or output regions before launching MME work.

State and persistence behavior: The file stores no runtime state; the macros name persistent hardware registers in DCORE0. Values written to these registers live in the device until reset or later driver/firmware programming overwrites them.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. These AGU offsets pair with the tensor/base-address descriptor headers in the same `dcore0_mme_ctrl_lo_arch_*` block.

Risks: The master/slave and input/output variants are adjacent and easy to confuse; writing the wrong ROI offset can redirect tensor reads or COUT writes. Because the file is generated, manual edits would drift from the hardware database.

Test signals: Build coverage catches missing macro names. Hardware or simulator tests should program MME descriptors using this IN0 slave lane, verify expected tensor addressing, and compare register dumps against the 0x40CB170-0x40CB180 address window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_in0_slave_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_in1_master_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_in1_master_regs.h

Purpose: Auto-generated Gaudi2 DCORE0 MME low-control AGU register map for the IN1 master address-generation core. It exposes five ROI base-offset MMIO addresses for the `MME_AGU_CORE` prototype at 0x40CB184-0x40CB194.

Important APIs/types/functions: There are no C functions or types. The exported API is the macro family `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN1_MASTER_ROI_BASE_OFFSET_0` (0x40CB184), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN1_MASTER_ROI_BASE_OFFSET_1` (0x40CB188), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN1_MASTER_ROI_BASE_OFFSET_2` (0x40CB18C), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN1_MASTER_ROI_BASE_OFFSET_3` (0x40CB190), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN1_MASTER_ROI_BASE_OFFSET_4` (0x40CB194), one register per ROI base-offset slot 0 through 4.

Control flow: No executable control flow exists in this header. Runtime flow is created by MME descriptor programming code that writes these offsets while configuring tensor or output regions before launching MME work.

State and persistence behavior: The file stores no runtime state; the macros name persistent hardware registers in DCORE0. Values written to these registers live in the device until reset or later driver/firmware programming overwrites them.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. These AGU offsets pair with the tensor/base-address descriptor headers in the same `dcore0_mme_ctrl_lo_arch_*` block.

Risks: The master/slave and input/output variants are adjacent and easy to confuse; writing the wrong ROI offset can redirect tensor reads or COUT writes. Because the file is generated, manual edits would drift from the hardware database.

Test signals: Build coverage catches missing macro names. Hardware or simulator tests should program MME descriptors using this IN1 master lane, verify expected tensor addressing, and compare register dumps against the 0x40CB184-0x40CB194 address window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_in1_master_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_in1_slave_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_in1_slave_regs.h

Purpose: Auto-generated Gaudi2 DCORE0 MME low-control AGU register map for the IN1 slave address-generation core. It exposes five ROI base-offset MMIO addresses for the `MME_AGU_CORE` prototype at 0x40CB198-0x40CB1A8.

Important APIs/types/functions: There are no C functions or types. The exported API is the macro family `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN1_SLAVE_ROI_BASE_OFFSET_0` (0x40CB198), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN1_SLAVE_ROI_BASE_OFFSET_1` (0x40CB19C), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN1_SLAVE_ROI_BASE_OFFSET_2` (0x40CB1A0), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN1_SLAVE_ROI_BASE_OFFSET_3` (0x40CB1A4), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN1_SLAVE_ROI_BASE_OFFSET_4` (0x40CB1A8), one register per ROI base-offset slot 0 through 4.

Control flow: No executable control flow exists in this header. Runtime flow is created by MME descriptor programming code that writes these offsets while configuring tensor or output regions before launching MME work.

State and persistence behavior: The file stores no runtime state; the macros name persistent hardware registers in DCORE0. Values written to these registers live in the device until reset or later driver/firmware programming overwrites them.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. These AGU offsets pair with the tensor/base-address descriptor headers in the same `dcore0_mme_ctrl_lo_arch_*` block.

Risks: The master/slave and input/output variants are adjacent and easy to confuse; writing the wrong ROI offset can redirect tensor reads or COUT writes. Because the file is generated, manual edits would drift from the hardware database.

Test signals: Build coverage catches missing macro names. Hardware or simulator tests should program MME descriptors using this IN1 slave lane, verify expected tensor addressing, and compare register dumps against the 0x40CB198-0x40CB1A8 address window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_in1_slave_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_in2_master_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_in2_master_regs.h

Purpose: Auto-generated Gaudi2 DCORE0 MME low-control AGU register map for the IN2 master address-generation core. It exposes five ROI base-offset MMIO addresses for the `MME_AGU_CORE` prototype at 0x40CB1AC-0x40CB1BC.

Important APIs/types/functions: There are no C functions or types. The exported API is the macro family `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN2_MASTER_ROI_BASE_OFFSET_0` (0x40CB1AC), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN2_MASTER_ROI_BASE_OFFSET_1` (0x40CB1B0), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN2_MASTER_ROI_BASE_OFFSET_2` (0x40CB1B4), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN2_MASTER_ROI_BASE_OFFSET_3` (0x40CB1B8), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN2_MASTER_ROI_BASE_OFFSET_4` (0x40CB1BC), one register per ROI base-offset slot 0 through 4.

Control flow: No executable control flow exists in this header. Runtime flow is created by MME descriptor programming code that writes these offsets while configuring tensor or output regions before launching MME work.

State and persistence behavior: The file stores no runtime state; the macros name persistent hardware registers in DCORE0. Values written to these registers live in the device until reset or later driver/firmware programming overwrites them.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. These AGU offsets pair with the tensor/base-address descriptor headers in the same `dcore0_mme_ctrl_lo_arch_*` block.

Risks: The master/slave and input/output variants are adjacent and easy to confuse; writing the wrong ROI offset can redirect tensor reads or COUT writes. Because the file is generated, manual edits would drift from the hardware database.

Test signals: Build coverage catches missing macro names. Hardware or simulator tests should program MME descriptors using this IN2 master lane, verify expected tensor addressing, and compare register dumps against the 0x40CB1AC-0x40CB1BC address window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_in2_master_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_in2_slave_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_in2_slave_regs.h

Purpose: Auto-generated Gaudi2 DCORE0 MME low-control AGU register map for the IN2 slave address-generation core. It exposes five ROI base-offset MMIO addresses for the `MME_AGU_CORE` prototype at 0x40CB1C0-0x40CB1D0.

Important APIs/types/functions: There are no C functions or types. The exported API is the macro family `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN2_SLAVE_ROI_BASE_OFFSET_0` (0x40CB1C0), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN2_SLAVE_ROI_BASE_OFFSET_1` (0x40CB1C4), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN2_SLAVE_ROI_BASE_OFFSET_2` (0x40CB1C8), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN2_SLAVE_ROI_BASE_OFFSET_3` (0x40CB1CC), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN2_SLAVE_ROI_BASE_OFFSET_4` (0x40CB1D0), one register per ROI base-offset slot 0 through 4.

Control flow: No executable control flow exists in this header. Runtime flow is created by MME descriptor programming code that writes these offsets while configuring tensor or output regions before launching MME work.

State and persistence behavior: The file stores no runtime state; the macros name persistent hardware registers in DCORE0. Values written to these registers live in the device until reset or later driver/firmware programming overwrites them.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. These AGU offsets pair with the tensor/base-address descriptor headers in the same `dcore0_mme_ctrl_lo_arch_*` block.

Risks: The master/slave and input/output variants are adjacent and easy to confuse; writing the wrong ROI offset can redirect tensor reads or COUT writes. Because the file is generated, manual edits would drift from the hardware database.

Test signals: Build coverage catches missing macro names. Hardware or simulator tests should program MME descriptors using this IN2 slave lane, verify expected tensor addressing, and compare register dumps against the 0x40CB1C0-0x40CB1D0 address window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_in2_slave_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_in3_master_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_in3_master_regs.h

Purpose: Auto-generated Gaudi2 DCORE0 MME low-control AGU register map for the IN3 master address-generation core. It exposes five ROI base-offset MMIO addresses for the `MME_AGU_CORE` prototype at 0x40CB1D4-0x40CB1E4.

Important APIs/types/functions: There are no C functions or types. The exported API is the macro family `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN3_MASTER_ROI_BASE_OFFSET_0` (0x40CB1D4), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN3_MASTER_ROI_BASE_OFFSET_1` (0x40CB1D8), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN3_MASTER_ROI_BASE_OFFSET_2` (0x40CB1DC), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN3_MASTER_ROI_BASE_OFFSET_3` (0x40CB1E0), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN3_MASTER_ROI_BASE_OFFSET_4` (0x40CB1E4), one register per ROI base-offset slot 0 through 4.

Control flow: No executable control flow exists in this header. Runtime flow is created by MME descriptor programming code that writes these offsets while configuring tensor or output regions before launching MME work.

State and persistence behavior: The file stores no runtime state; the macros name persistent hardware registers in DCORE0. Values written to these registers live in the device until reset or later driver/firmware programming overwrites them.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. These AGU offsets pair with the tensor/base-address descriptor headers in the same `dcore0_mme_ctrl_lo_arch_*` block.

Risks: The master/slave and input/output variants are adjacent and easy to confuse; writing the wrong ROI offset can redirect tensor reads or COUT writes. Because the file is generated, manual edits would drift from the hardware database.

Test signals: Build coverage catches missing macro names. Hardware or simulator tests should program MME descriptors using this IN3 master lane, verify expected tensor addressing, and compare register dumps against the 0x40CB1D4-0x40CB1E4 address window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_in3_master_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_in3_slave_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_in3_slave_regs.h

Purpose: Auto-generated Gaudi2 DCORE0 MME low-control AGU register map for the IN3 slave address-generation core. It exposes five ROI base-offset MMIO addresses for the `MME_AGU_CORE` prototype at 0x40CB1E8-0x40CB1F8.

Important APIs/types/functions: There are no C functions or types. The exported API is the macro family `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN3_SLAVE_ROI_BASE_OFFSET_0` (0x40CB1E8), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN3_SLAVE_ROI_BASE_OFFSET_1` (0x40CB1EC), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN3_SLAVE_ROI_BASE_OFFSET_2` (0x40CB1F0), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN3_SLAVE_ROI_BASE_OFFSET_3` (0x40CB1F4), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN3_SLAVE_ROI_BASE_OFFSET_4` (0x40CB1F8), one register per ROI base-offset slot 0 through 4.

Control flow: No executable control flow exists in this header. Runtime flow is created by MME descriptor programming code that writes these offsets while configuring tensor or output regions before launching MME work.

State and persistence behavior: The file stores no runtime state; the macros name persistent hardware registers in DCORE0. Values written to these registers live in the device until reset or later driver/firmware programming overwrites them.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. These AGU offsets pair with the tensor/base-address descriptor headers in the same `dcore0_mme_ctrl_lo_arch_*` block.

Risks: The master/slave and input/output variants are adjacent and easy to confuse; writing the wrong ROI offset can redirect tensor reads or COUT writes. Because the file is generated, manual edits would drift from the hardware database.

Test signals: Build coverage catches missing macro names. Hardware or simulator tests should program MME descriptors using this IN3 slave lane, verify expected tensor addressing, and compare register dumps against the 0x40CB1E8-0x40CB1F8 address window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_in3_slave_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_in4_master_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_in4_master_regs.h

Purpose: Auto-generated Gaudi2 DCORE0 MME low-control AGU register map for the IN4 master address-generation core. It exposes five ROI base-offset MMIO addresses for the `MME_AGU_CORE` prototype at 0x40CB1FC-0x40CB20C.

Important APIs/types/functions: There are no C functions or types. The exported API is the macro family `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN4_MASTER_ROI_BASE_OFFSET_0` (0x40CB1FC), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN4_MASTER_ROI_BASE_OFFSET_1` (0x40CB200), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN4_MASTER_ROI_BASE_OFFSET_2` (0x40CB204), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN4_MASTER_ROI_BASE_OFFSET_3` (0x40CB208), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN4_MASTER_ROI_BASE_OFFSET_4` (0x40CB20C), one register per ROI base-offset slot 0 through 4.

Control flow: No executable control flow exists in this header. Runtime flow is created by MME descriptor programming code that writes these offsets while configuring tensor or output regions before launching MME work.

State and persistence behavior: The file stores no runtime state; the macros name persistent hardware registers in DCORE0. Values written to these registers live in the device until reset or later driver/firmware programming overwrites them.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. These AGU offsets pair with the tensor/base-address descriptor headers in the same `dcore0_mme_ctrl_lo_arch_*` block.

Risks: The master/slave and input/output variants are adjacent and easy to confuse; writing the wrong ROI offset can redirect tensor reads or COUT writes. Because the file is generated, manual edits would drift from the hardware database.

Test signals: Build coverage catches missing macro names. Hardware or simulator tests should program MME descriptors using this IN4 master lane, verify expected tensor addressing, and compare register dumps against the 0x40CB1FC-0x40CB20C address window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_in4_master_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_in4_slave_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_in4_slave_regs.h

Purpose: Auto-generated Gaudi2 DCORE0 MME low-control AGU register map for the IN4 slave address-generation core. It exposes five ROI base-offset MMIO addresses for the `MME_AGU_CORE` prototype at 0x40CB210-0x40CB220.

Important APIs/types/functions: There are no C functions or types. The exported API is the macro family `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN4_SLAVE_ROI_BASE_OFFSET_0` (0x40CB210), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN4_SLAVE_ROI_BASE_OFFSET_1` (0x40CB214), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN4_SLAVE_ROI_BASE_OFFSET_2` (0x40CB218), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN4_SLAVE_ROI_BASE_OFFSET_3` (0x40CB21C), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN4_SLAVE_ROI_BASE_OFFSET_4` (0x40CB220), one register per ROI base-offset slot 0 through 4.

Control flow: No executable control flow exists in this header. Runtime flow is created by MME descriptor programming code that writes these offsets while configuring tensor or output regions before launching MME work.

State and persistence behavior: The file stores no runtime state; the macros name persistent hardware registers in DCORE0. Values written to these registers live in the device until reset or later driver/firmware programming overwrites them.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. These AGU offsets pair with the tensor/base-address descriptor headers in the same `dcore0_mme_ctrl_lo_arch_*` block.

Risks: The master/slave and input/output variants are adjacent and easy to confuse; writing the wrong ROI offset can redirect tensor reads or COUT writes. Because the file is generated, manual edits would drift from the hardware database.

Test signals: Build coverage catches missing macro names. Hardware or simulator tests should program MME descriptors using this IN4 slave lane, verify expected tensor addressing, and compare register dumps against the 0x40CB210-0x40CB220 address window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_in4_slave_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_base_addr_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_base_addr_regs.h

Purpose: Defines the DCORE0 MME low-control base-address descriptor registers for the MME address descriptor prototype. It maps low/high address pairs for COUT1, COUT0, tensor A, and tensor B at 0x40CB008-0x40CB024.

Important APIs/types/functions: The public surface is eight `mmDCORE0_MME_CTRL_LO_ARCH_BASE_ADDR_*` macros: `mmDCORE0_MME_CTRL_LO_ARCH_BASE_ADDR_COUT1_LOW` (0x40CB008), `mmDCORE0_MME_CTRL_LO_ARCH_BASE_ADDR_COUT1_HIGH` (0x40CB00C), `mmDCORE0_MME_CTRL_LO_ARCH_BASE_ADDR_COUT0_LOW` (0x40CB010), `mmDCORE0_MME_CTRL_LO_ARCH_BASE_ADDR_COUT0_HIGH` (0x40CB014), `mmDCORE0_MME_CTRL_LO_ARCH_BASE_ADDR_A_LOW` (0x40CB018), and `mmDCORE0_MME_CTRL_LO_ARCH_BASE_ADDR_B_HIGH` (0x40CB024). There are no structs, functions, or inline helpers.

Control flow: MME setup code writes these base address registers before tensor dimension, stride, and AGU offset registers are consumed by the hardware launch path.

State and persistence behavior: The header is stateless. Programmed register values represent device-local descriptor state and persist until the MME control block is reset or reprogrammed.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. It integrates directly with tensor A/B/COUT descriptor and AGU offset headers.

Risks: Low/high register ordering and COUT0/COUT1 selection are correctness-critical for 64-bit device addresses. Stale base addresses can cause DMA to the wrong memory region.

Test signals: Descriptor programming tests should validate 64-bit address split/merge, COUT0/COUT1 selection, and register dump comparison for the 0x40CB008-0x40CB024 descriptor area.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_base_addr_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_non_tensor_end_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_non_tensor_end_regs.h

Purpose: Defines the closing non-tensor descriptor register addresses for DCORE0 MME low-control programming. It covers convolution metadata, loop/iteration fields, padding values, signal masks, store/rounding controls, activation enables, rates, and work-load id at 0x40CB280-0x40CB2DC.

Important APIs/types/functions: Exports 24 `mmDCORE0_MME_CTRL_LO_ARCH_NON_TENSOR_END_*` macros, represented by `mmDCORE0_MME_CTRL_LO_ARCH_NON_TENSOR_END_CONV_KERNEL_SIZE_MINUS_1` (0x40CB280), `mmDCORE0_MME_CTRL_LO_ARCH_NON_TENSOR_END_CONV_LOW` (0x40CB284), `mmDCORE0_MME_CTRL_LO_ARCH_NON_TENSOR_END_CONV_HIGH` (0x40CB288), `mmDCORE0_MME_CTRL_LO_ARCH_NON_TENSOR_END_OUTER_LOOP` (0x40CB28C), `mmDCORE0_MME_CTRL_LO_ARCH_NON_TENSOR_END_NUM_ITERATIONS_MINUS_1` (0x40CB290), and `mmDCORE0_MME_CTRL_LO_ARCH_NON_TENSOR_END_WKL_ID` (0x40CB2DC). There are no functions or data structures.

Control flow: MME descriptor code writes these fields after base, tensor, and non-tensor-start words and before issuing `mmDCORE0_MME_CTRL_LO_CMD`.

State and persistence behavior: The header is compile-time metadata only. Hardware register state controls the next or current MME operation until reprogramming or reset.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. The fields tie MME computation semantics to sync objects and output storage behavior.

Risks: Off-by-one fields such as kernel size and iterations are named as minus-one values, so caller-side encoding errors can silently change shape. Signal mask and store enable fields affect completion behavior and output visibility.

Test signals: Convolution and GEMM descriptor tests should cover padding, rounding, activation, store-enable, work-load-id, signal-mask, and iteration edge cases with register readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_non_tensor_end_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_non_tensor_start_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_non_tensor_start_regs.h

Purpose: Provides the opening non-tensor descriptor registers for DCORE0 MME low-control architecture programming. The block covers brains/header low/high words and EUS master/slave controls at 0x40CB028-0x40CB03C.

Important APIs/types/functions: Exports six `mmDCORE0_MME_CTRL_LO_ARCH_NON_TENSOR_START_*` address macros including `mmDCORE0_MME_CTRL_LO_ARCH_NON_TENSOR_START_BRAINS_LOW` (0x40CB028), `mmDCORE0_MME_CTRL_LO_ARCH_NON_TENSOR_START_BRAINS_HIGH` (0x40CB02C), `mmDCORE0_MME_CTRL_LO_ARCH_NON_TENSOR_START_HEADER_LOW` (0x40CB030), `mmDCORE0_MME_CTRL_LO_ARCH_NON_TENSOR_START_HEADER_HIGH` (0x40CB034), `mmDCORE0_MME_CTRL_LO_ARCH_NON_TENSOR_START_EUS_MASTER` (0x40CB038), `mmDCORE0_MME_CTRL_LO_ARCH_NON_TENSOR_START_EUS_SLAVE` (0x40CB03C). No code or types are defined.

Control flow: Firmware or driver descriptor assembly writes these registers before the detailed tensor and non-tensor end fields to seed MME command metadata.

State and persistence behavior: No software state is held. Register contents are device configuration state for the current MME work descriptor and are overwritten by later work or reset.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. It complements `dcore0_mme_ctrl_lo_arch_non_tensor_end_regs.h` and the main `dcore0_mme_ctrl_lo_regs.h` command/status block.

Risks: Header/brains fields are opaque hardware contract words; incorrect bit packing in callers can make a descriptor invalid even though the macro address is correct.

Test signals: Validate generated descriptor images against firmware/hardware specs, read back the start registers after programming, and run MME smoke tests that exercise both EUS master and slave paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_non_tensor_start_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_tensor_a_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_tensor_a_regs.h

Purpose: Defines the DCORE0 MME tensor A descriptor register addresses for tensor geometry and addressing. The block spans valid-elements, loop stride, ROI size, spatial stride, and start-offset fields at 0x40CB040-0x40CB094.

Important APIs/types/functions: Exports 22 `mmDCORE0_MME_CTRL_LO_ARCH_TENSOR_A_*` macros, including `mmDCORE0_MME_CTRL_LO_ARCH_TENSOR_A_VALID_ELEMENTS_0` (0x40CB040), `mmDCORE0_MME_CTRL_LO_ARCH_TENSOR_A_VALID_ELEMENTS_1` (0x40CB044), `mmDCORE0_MME_CTRL_LO_ARCH_TENSOR_A_VALID_ELEMENTS_2` (0x40CB048), `mmDCORE0_MME_CTRL_LO_ARCH_TENSOR_A_VALID_ELEMENTS_3` (0x40CB04C), `mmDCORE0_MME_CTRL_LO_ARCH_TENSOR_A_VALID_ELEMENTS_4` (0x40CB050), and `mmDCORE0_MME_CTRL_LO_ARCH_TENSOR_A_START_OFFSET_3` (0x40CB094). No executable APIs are present.

Control flow: Descriptor construction writes tensor shape and stride registers before AGU and command launch logic uses them to generate memory transactions.

State and persistence behavior: Software state is absent; programmed values are hardware descriptor state for tensor A and remain until reset or reprogramming.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. Tensor A registers combine with base-address and AGU ROI-offset registers to define actual memory access patterns.

Risks: Tensor A, B, and COUT layouts are structurally similar but occupy different address windows; mixing them causes incorrect reads or output placement. Dimensional fields have fixed register counts, so caller loops must match the hardware-supported rank.

Test signals: Shape/stride unit tests, descriptor dump validation, and MME execution tests with nontrivial ROI sizes and start offsets are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_tensor_a_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_tensor_b_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_tensor_b_regs.h

Purpose: Defines the DCORE0 MME tensor B descriptor register addresses for tensor geometry and addressing. The block spans valid-elements, loop stride, ROI size, spatial stride, and start-offset fields at 0x40CB098-0x40CB0EC.

Important APIs/types/functions: Exports 22 `mmDCORE0_MME_CTRL_LO_ARCH_TENSOR_B_*` macros, including `mmDCORE0_MME_CTRL_LO_ARCH_TENSOR_B_VALID_ELEMENTS_0` (0x40CB098), `mmDCORE0_MME_CTRL_LO_ARCH_TENSOR_B_VALID_ELEMENTS_1` (0x40CB09C), `mmDCORE0_MME_CTRL_LO_ARCH_TENSOR_B_VALID_ELEMENTS_2` (0x40CB0A0), `mmDCORE0_MME_CTRL_LO_ARCH_TENSOR_B_VALID_ELEMENTS_3` (0x40CB0A4), `mmDCORE0_MME_CTRL_LO_ARCH_TENSOR_B_VALID_ELEMENTS_4` (0x40CB0A8), and `mmDCORE0_MME_CTRL_LO_ARCH_TENSOR_B_START_OFFSET_3` (0x40CB0EC). No executable APIs are present.

Control flow: Descriptor construction writes tensor shape and stride registers before AGU and command launch logic uses them to generate memory transactions.

State and persistence behavior: Software state is absent; programmed values are hardware descriptor state for tensor B and remain until reset or reprogramming.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. Tensor B registers combine with base-address and AGU ROI-offset registers to define actual memory access patterns.

Risks: Tensor A, B, and COUT layouts are structurally similar but occupy different address windows; mixing them causes incorrect reads or output placement. Dimensional fields have fixed register counts, so caller loops must match the hardware-supported rank.

Test signals: Shape/stride unit tests, descriptor dump validation, and MME execution tests with nontrivial ROI sizes and start offsets are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_tensor_b_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_tensor_cout_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_tensor_cout_regs.h

Purpose: Defines the DCORE0 MME tensor COUT descriptor register addresses for tensor geometry and addressing. The block spans valid-elements, loop stride, ROI size, spatial stride, and start-offset fields at 0x40CB0F0-0x40CB144.

Important APIs/types/functions: Exports 22 `mmDCORE0_MME_CTRL_LO_ARCH_TENSOR_COUT_*` macros, including `mmDCORE0_MME_CTRL_LO_ARCH_TENSOR_COUT_VALID_ELEMENTS_0` (0x40CB0F0), `mmDCORE0_MME_CTRL_LO_ARCH_TENSOR_COUT_VALID_ELEMENTS_1` (0x40CB0F4), `mmDCORE0_MME_CTRL_LO_ARCH_TENSOR_COUT_VALID_ELEMENTS_2` (0x40CB0F8), `mmDCORE0_MME_CTRL_LO_ARCH_TENSOR_COUT_VALID_ELEMENTS_3` (0x40CB0FC), `mmDCORE0_MME_CTRL_LO_ARCH_TENSOR_COUT_VALID_ELEMENTS_4` (0x40CB100), and `mmDCORE0_MME_CTRL_LO_ARCH_TENSOR_COUT_START_OFFSET_3` (0x40CB144). No executable APIs are present.

Control flow: Descriptor construction writes tensor shape and stride registers before AGU and command launch logic uses them to generate memory transactions.

State and persistence behavior: Software state is absent; programmed values are hardware descriptor state for tensor COUT and remain until reset or reprogramming.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. Tensor COUT registers combine with base-address and AGU ROI-offset registers to define actual memory access patterns.

Risks: Tensor A, B, and COUT layouts are structurally similar but occupy different address windows; mixing them causes incorrect reads or output placement. Dimensional fields have fixed register counts, so caller loops must match the hardware-supported rank.

Test signals: Shape/stride unit tests, descriptor dump validation, and MME execution tests with nontrivial ROI sizes and start offsets are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_tensor_cout_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_masks.h

Purpose: Supplies shift and mask constants for the DCORE0 MME low-control register block. It describes bitfields for architecture status, command control, sync-object FIFO thresholds, logging shadows, redundancy, EUS rollup/protection, PCU rate limiting, dummy values, EU/SBTE controls, counters, debug words, and ETF memory wrap fields.

Important APIs/types/functions: Exports 302 `DCORE0_MME_CTRL_LO_*_{SHIFT,MASK}` constants rather than MMIO addresses. Representative fields include `DCORE0_MME_CTRL_LO_ARCH_STATUS_AGU_IN_SHIFT` (0), `DCORE0_MME_CTRL_LO_ARCH_STATUS_AGU_IN_MASK` (0x1F), `DCORE0_MME_CTRL_LO_ARCH_STATUS_EU_SHIFT` (5), `DCORE0_MME_CTRL_LO_ARCH_STATUS_EU_MASK` (0x20), `DCORE0_MME_CTRL_LO_ARCH_STATUS_AP_SHIFT` (6), and `DCORE0_MME_CTRL_LO_ETF_MEM_WRAP_RM_V_MASK` (0x3FFFFFFF).

Control flow: There is no code. Register accessors use these constants to pack writes and unpack reads for the companion `dcore0_mme_ctrl_lo_regs.h` address macros.

State and persistence behavior: The header has no state. Correct use determines how software mutates or interprets persistent hardware state in the MME low-control block.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. It is tightly coupled to the generated address header and any debug, reset, or performance logic that decodes MME state.

Risks: A stale mask paired with a newer address map can corrupt unrelated bits. Several fields govern clock gating, rate limiting, error handling, and protection, so read-modify-write discipline is required.

Test signals: Compile checks for macro availability, register bitfield encode/decode unit tests where available, hardware register readback after masked writes, and MME error-injection or performance-counter tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_mme_axuser_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_mme_axuser_regs.h

Purpose: Defines AXUSER attribute register addresses for the `MME_CTRL_LO_MME_AXUSER` DCORE0 master interface. The registers cover high-bandwidth and low-bandwidth ASID, MMU bypass, strong ordering, snoop, write-reduction, QoS, core, reserved, lock/coordination, and override fields at 0x40CBE00-0x40CBE4C.

Important APIs/types/functions: Exports 19 `mmDCORE0_*_AXUSER_*` address macros, including `mmDCORE0_MME_CTRL_LO_MME_AXUSER_HB_ASID` (0x40CBE00), `mmDCORE0_MME_CTRL_LO_MME_AXUSER_HB_MMU_BP` (0x40CBE04), `mmDCORE0_MME_CTRL_LO_MME_AXUSER_HB_STRONG_ORDER` (0x40CBE08), `mmDCORE0_MME_CTRL_LO_MME_AXUSER_HB_NO_SNOOP` (0x40CBE0C), `mmDCORE0_MME_CTRL_LO_MME_AXUSER_HB_WR_REDUCTION` (0x40CBE10), and `mmDCORE0_MME_CTRL_LO_MME_AXUSER_LB_OVRD` (0x40CBE4C). There are no functions or C types.

Control flow: Initialization, security, or firmware setup code writes these registers before the associated engine issues AXI transactions; runtime data movement then carries the programmed AXUSER attributes.

State and persistence behavior: Attribute values are hardware configuration state and persist until reset or reprogramming. The header itself is pure compile-time metadata.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. It integrates with MMU/security policy, cache/snoop behavior, and engine-specific DMA paths.

Risks: Incorrect ASID, MMU bypass, or strong-order settings can break isolation or memory ordering. Secured and nonsecured variants must not be interchanged.

Test signals: Security allowlist validation, MMU translation tests, protected/unprotected DMA smoke tests, and register readback of AXUSER setup for this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_mme_axuser_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_regs.h

Purpose: Defines the main DCORE0 MME low-control MMIO register addresses. The block includes architecture status and command registers, sync-object programming, descriptor shortcuts, QM stall/log/shadow controls, EUS/PCU tuning, protection, EU/SBTE controls, counters, debug, clock, and ETF memory wrap addresses at 0x40CB000-0x40CB4EC.

Important APIs/types/functions: Exports 70 `mmDCORE0_MME_CTRL_LO_*` address macros, represented by `mmDCORE0_MME_CTRL_LO_ARCH_STATUS` (0x40CB000), `mmDCORE0_MME_CTRL_LO_CMD` (0x40CB004), `mmDCORE0_MME_CTRL_LO_ARCH_SYNC_OBJ_DW0` (0x40CB148), `mmDCORE0_MME_CTRL_LO_ARCH_SYNC_OBJ_ADDR0` (0x40CB14C), `mmDCORE0_MME_CTRL_LO_ARCH_SYNC_OBJ_VAL0` (0x40CB150), and `mmDCORE0_MME_CTRL_LO_ETF_MEM_WRAP_RM` (0x40CB4EC). There are no functions or types.

Control flow: Driver and firmware code reads status, programs descriptor-related registers, tunes control fields through mask constants, then writes command/control registers to launch or manage MME work.

State and persistence behavior: The file itself is stateless. The named registers hold live device state such as command, status, thresholds, debug counters, and protection settings until reset or explicit writes.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. `gaudi2_security.c` references this block in security/privilege region handling, and companion mask headers define field packing.

Risks: This is a central control surface; wrong addresses can stall the queue manager, alter protection, or misconfigure rate limiting. Generated-file drift against silicon is high impact.

Test signals: Gaudi2 driver build, security-region list validation, MME bring-up tests, command/status polling tests, register dump decode, and error-injection around QM stall and SBTE/EU fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_qm_arc_acp_eng_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_qm_arc_acp_eng_regs.h

Purpose: Defines DCORE0 MME QM ARC ACP engine registers. The map exposes 64-entry ACP producer, consumer, priority, and mask arrays plus selected-queue, grant-weight/counter, debug count, and debug control registers at 0x40CF000-0x40CF43C.

Important APIs/types/functions: Exports 272 `mmDCORE0_MME_QM_ARC_ACP_ENG_*` address macros, including `mmDCORE0_MME_QM_ARC_ACP_ENG_ACP_PI_REG_0` (0x40CF000), `mmDCORE0_MME_QM_ARC_ACP_ENG_ACP_PI_REG_1` (0x40CF004), `mmDCORE0_MME_QM_ARC_ACP_ENG_ACP_PI_REG_2` (0x40CF008), `mmDCORE0_MME_QM_ARC_ACP_ENG_ACP_PI_REG_3` (0x40CF00C), `mmDCORE0_MME_QM_ARC_ACP_ENG_ACP_PI_REG_4` (0x40CF010), and `mmDCORE0_MME_QM_ARC_ACP_ENG_ACP_DBG_REG` (0x40CF43C). No executable API is present.

Control flow: ARC/QMAN firmware or driver debug paths use these registers to observe or configure ACP queue arbitration and priority behavior.

State and persistence behavior: Register contents are live ACP queue/arbitration state. The header has no state and only binds macro names to addresses.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. It integrates with MME QM ARC firmware, arbitration diagnostics, and privileged register-region policy.

Risks: The 64-entry arrays must be indexed consistently; off-by-one register selection changes queue priority or mask state. Debug counters may be volatile and require stable sampling.

Test signals: ARC firmware startup, ACP queue traffic tests, priority/weight arbitration tests, debug-counter readback, and security allowlist checks for the 0x40CF000-0x40CF43C window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_qm_arc_acp_eng_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_qm_arc_aux_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_qm_arc_aux_regs.h

Purpose: Defines DCORE0 MME QM ARC auxiliary registers for run/halt, reset vector, debug mode, cluster identity, interrupts, scratchpads, ARC regions, DCCM queues, CID offsets, LBU/CBU counters, fork address masks, and upper-DCCM control at 0x40C8100-0x40C8920.

Important APIs/types/functions: Exports 284 `mmDCORE0_MME_QM_ARC_AUX_*` address macros. Repeated families include 16 software interrupts, 16 ARC region configs, eight scratchpads, eight DCCM queue descriptors, and representative macros `mmDCORE0_MME_QM_ARC_AUX_RUN_HALT_REQ` (0x40C8100), `mmDCORE0_MME_QM_ARC_AUX_RUN_HALT_ACK` (0x40C8104), `mmDCORE0_MME_QM_ARC_AUX_RST_VEC_ADDR` (0x40C8108), `mmDCORE0_MME_QM_ARC_AUX_DBG_MODE` (0x40C810C), `mmDCORE0_MME_QM_ARC_AUX_CLUSTER_NUM` (0x40C8110), and `mmDCORE0_MME_QM_ARC_AUX_MME_ARC_UPPER_DCCM_EN` (0x40C8920).

Control flow: Device bring-up and recovery request ARC halt/reset, configure memory regions and DCCM queues, then monitor acknowledgements, interrupts, and bus counters while QMAN firmware runs.

State and persistence behavior: The header is stateless; the hardware registers hold ARC processor state, queue metadata, scratch values, interrupts, and counters until firmware or reset changes them.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. `gaudi2_security.c` explicitly references ranges in this header for protected access windows and ARC control.

Risks: Run/halt and reset registers affect firmware liveness. DCCM queue base/size/counter mistakes can break firmware communication, and security ranges must not expose more ARC control than intended.

Test signals: ARC boot/halt/reset tests, firmware queue communication, interrupt delivery, scratchpad preservation during expected flows, counter readback, and protected-mode access validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_qm_arc_aux_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_qm_arc_dup_eng_axuser_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_qm_arc_dup_eng_axuser_regs.h

Purpose: Defines AXUSER attribute register addresses for the `MME_QM_ARC_DUP_ENG_AXUSER` DCORE0 master interface. The registers cover high-bandwidth and low-bandwidth ASID, MMU bypass, strong ordering, snoop, write-reduction, QoS, core, reserved, lock/coordination, and override fields at 0x40C9900-0x40C994C.

Important APIs/types/functions: Exports 19 `mmDCORE0_*_AXUSER_*` address macros, including `mmDCORE0_MME_QM_ARC_DUP_ENG_AXUSER_HB_ASID` (0x40C9900), `mmDCORE0_MME_QM_ARC_DUP_ENG_AXUSER_HB_MMU_BP` (0x40C9904), `mmDCORE0_MME_QM_ARC_DUP_ENG_AXUSER_HB_STRONG_ORDER` (0x40C9908), `mmDCORE0_MME_QM_ARC_DUP_ENG_AXUSER_HB_NO_SNOOP` (0x40C990C), `mmDCORE0_MME_QM_ARC_DUP_ENG_AXUSER_HB_WR_REDUCTION` (0x40C9910), and `mmDCORE0_MME_QM_ARC_DUP_ENG_AXUSER_LB_OVRD` (0x40C994C). There are no functions or C types.

Control flow: Initialization, security, or firmware setup code writes these registers before the associated engine issues AXI transactions; runtime data movement then carries the programmed AXUSER attributes.

State and persistence behavior: Attribute values are hardware configuration state and persist until reset or reprogramming. The header itself is pure compile-time metadata.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. It integrates with MMU/security policy, cache/snoop behavior, and engine-specific DMA paths.

Risks: Incorrect ASID, MMU bypass, or strong-order settings can break isolation or memory ordering. Secured and nonsecured variants must not be interchanged.

Test signals: Security allowlist validation, MMU translation tests, protected/unprotected DMA smoke tests, and register readback of AXUSER setup for this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_qm_arc_dup_eng_axuser_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_qm_arc_dup_eng_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_qm_arc_dup_eng_regs.h

Purpose: Defines DCORE0 MME QM ARC duplicate-engine registers. The block maps duplicate TPC engine target addresses, NIC duplication controls, LBU addresses, dup mask/destination fields, and 64 ARC context-id offsets at 0x40C9000-0x40C96B0.

Important APIs/types/functions: Exports 276 `mmDCORE0_MME_QM_ARC_DUP_ENG_*` address macros, represented by `mmDCORE0_MME_QM_ARC_DUP_ENG_DUP_TPC_ENG_ADDR_0` (0x40C9000), `mmDCORE0_MME_QM_ARC_DUP_ENG_DUP_TPC_ENG_ADDR_1` (0x40C9004), `mmDCORE0_MME_QM_ARC_DUP_ENG_DUP_TPC_ENG_ADDR_2` (0x40C9008), `mmDCORE0_MME_QM_ARC_DUP_ENG_DUP_TPC_ENG_ADDR_3` (0x40C900C), `mmDCORE0_MME_QM_ARC_DUP_ENG_DUP_TPC_ENG_ADDR_4` (0x40C9010), and `mmDCORE0_MME_QM_ARC_DUP_ENG_ARC_CID_OFFSET_63` (0x40C96B0). There are no functions or data types.

Control flow: Firmware or setup code configures duplicate-engine destinations and context offsets before queue-manager ARC traffic is replicated or routed.

State and persistence behavior: The macros are static. Hardware register state controls duplication/routing behavior and persists until reset or reconfiguration.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. It integrates with ARC firmware messaging, TPC/NIC routing, and the AXUSER attributes in the matching duplicate-engine AXUSER header.

Risks: Misprogrammed duplicate destinations or context offsets can route messages to the wrong engine. The 64-entry CID-offset array is sensitive to consistent indexing.

Test signals: Firmware routing tests, duplicate-engine traffic validation, CID-offset readback, security-region validation, and negative tests for disabled/invalid destination masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_qm_arc_dup_eng_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_qm_axuser_nonsecured_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_qm_axuser_nonsecured_regs.h

Purpose: Auto-generated register definition header for the `AXUSER` hardware block. It exports macro constants over 0x40CAB80-0x40CABCC.

Important APIs/types/functions: Exported constants include `mmDCORE0_MME_QM_AXUSER_NONSECURED_HB_ASID` (0x40CAB80), `mmDCORE0_MME_QM_AXUSER_NONSECURED_HB_MMU_BP` (0x40CAB84), `mmDCORE0_MME_QM_AXUSER_NONSECURED_HB_STRONG_ORDER` (0x40CAB88), `mmDCORE0_MME_QM_AXUSER_NONSECURED_HB_NO_SNOOP` (0x40CAB8C), `mmDCORE0_MME_QM_AXUSER_NONSECURED_HB_WR_REDUCTION` (0x40CAB90), and `mmDCORE0_MME_QM_AXUSER_NONSECURED_LB_OVRD` (0x40CABCC). No functions or C types are defined.

Control flow: None in this header; callers create runtime flow by using the macros in register accesses.

State and persistence behavior: Stateless compile-time metadata; hardware state lives in the addressed registers.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths.

Risks: Generated address drift or use of a wrong sibling block can misprogram hardware.

Test signals: Build coverage, register dump validation, and block-specific hardware smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_qm_axuser_nonsecured_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_qm_axuser_secured_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_qm_axuser_secured_regs.h

Purpose: Auto-generated register definition header for the `AXUSER` hardware block. It exports macro constants over 0x40CAB00-0x40CAB4C.

Important APIs/types/functions: Exported constants include `mmDCORE0_MME_QM_AXUSER_SECURED_HB_ASID` (0x40CAB00), `mmDCORE0_MME_QM_AXUSER_SECURED_HB_MMU_BP` (0x40CAB04), `mmDCORE0_MME_QM_AXUSER_SECURED_HB_STRONG_ORDER` (0x40CAB08), `mmDCORE0_MME_QM_AXUSER_SECURED_HB_NO_SNOOP` (0x40CAB0C), `mmDCORE0_MME_QM_AXUSER_SECURED_HB_WR_REDUCTION` (0x40CAB10), and `mmDCORE0_MME_QM_AXUSER_SECURED_LB_OVRD` (0x40CAB4C). No functions or C types are defined.

Control flow: None in this header; callers create runtime flow by using the macros in register accesses.

State and persistence behavior: Stateless compile-time metadata; hardware state lives in the addressed registers.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths.

Risks: Generated address drift or use of a wrong sibling block can misprogram hardware.

Test signals: Build coverage, register dump validation, and block-specific hardware smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_qm_axuser_secured_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_qm_cgm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_qm_cgm_regs.h

Purpose: Defines the tiny DCORE0 MME QMAN clock-gating/control-management register block. It exposes CGM configuration, status, and secondary configuration addresses at 0x40CAD80-0x40CAD88.

Important APIs/types/functions: The exported API is three address macros: `mmDCORE0_MME_QM_CGM_CFG` (0x40CAD80), `mmDCORE0_MME_QM_CGM_STS` (0x40CAD84), `mmDCORE0_MME_QM_CGM_CFG1` (0x40CAD88). No functions or types are defined.

Control flow: Power-management or bring-up code writes CGM config, observes status, and may adjust the second config register as part of QMAN clock gating.

State and persistence behavior: The header has no state. CGM registers hold hardware power/clock-gating state until reset or a later write.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. It integrates with QMAN power management and diagnostics.

Risks: Bad CGM programming can gate clocks while QMAN is active or leave clocks ungated. Status sampling must account for hardware transition latency.

Test signals: Clock-gating enable/disable tests, QMAN activity across low-power transitions, and register readback for config/status consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_qm_cgm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_qm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_qm_regs.h

Purpose: Defines the main DCORE0 MME queue-manager MMIO map for the QMAN prototype. It covers global config/status/error registers, producer queues, completion queues, command processors, fence counters, ARC queues, arbiter state, write64 bases, AWUSER messages, PQC status, and performance-counter configuration at 0x40CA000-0x40CAD70.

Important APIs/types/functions: Exports 517 `mmDCORE0_MME_QM_*` address macros. Dense families include four PQs, five CQs/CP lanes, four fence groups per lane, 64 arbiter availability/choice entries, and representative macros `mmDCORE0_MME_QM_GLBL_CFG0` (0x40CA000), `mmDCORE0_MME_QM_GLBL_CFG1` (0x40CA004), `mmDCORE0_MME_QM_GLBL_CFG2` (0x40CA008), `mmDCORE0_MME_QM_GLBL_ERR_CFG` (0x40CA00C), `mmDCORE0_MME_QM_GLBL_ERR_CFG1` (0x40CA010), and `mmDCORE0_MME_QM_PERF_CNT_CFG` (0x40CAD70).

Control flow: Queue setup code programs PQ/CQ base, size, pointer, command-processor, fence, and arbiter registers; firmware and hardware then consume queue entries and update status/counters.

State and persistence behavior: This header is stateless, but the named registers contain live queue-manager state: indices, credits, fences, errors, arbitration choices, and performance counters. Values are reset or reinitialized during device bring-up/recovery.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. `gaudi2_security.c` references this block and individual CQ/CP/fence registers for privileged-region definitions. It also ties to ARC auxiliary and duplicate-engine headers.

Risks: Queue pointer, size, and fence address errors can deadlock command submission or corrupt completion handling. Security allowlists must include exactly the intended control/status windows.

Test signals: Queue-manager bring-up, command submission/completion tests, fence signaling, error interrupt injection, performance-counter readback, and security-region validation covering the CQ/CP/ARB address families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_qm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_sbte0_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_sbte0_masks.h

Purpose: Provides bitfield shifts and masks for the DCORE0 MME SBTE0 stream/bus-transfer engine. Fields cover maximum data/metadata size, force miss, ARUSER/ARCACHE attributes, occupancy and inflight controls, protection, interrupts, rate limiter, clock gating, stall, status drop count, and interface valid/ready debug.

Important APIs/types/functions: Exports 48 `DCORE0_MME_SBTE0_*` field constants, including `DCORE0_MME_SBTE0_MAX_SIZE_DATA_SHIFT` (0), `DCORE0_MME_SBTE0_MAX_SIZE_DATA_MASK` (0xFFFF), `DCORE0_MME_SBTE0_MAX_SIZE_MD_SHIFT` (16), `DCORE0_MME_SBTE0_MAX_SIZE_MD_MASK` (0xFFFF0000), `DCORE0_MME_SBTE0_FORCE_MISS_R_SHIFT` (0), and `DCORE0_MME_SBTE0_INTF_RDY_DBG_RDY_MASK` (0xFFFFFFFF). No code is present.

Control flow: There is no executable flow. Callers use the masks with SBTE0 register addresses from companion headers to configure transfer behavior and decode status.

State and persistence behavior: Compile-time constants only; they guide mutation and interpretation of SBTE0 hardware state.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. It integrates with MME data movement, protection setup, rate limiting, and interrupt handling.

Risks: Incorrect ARUSER, protection, or rate-limit bit packing can cause memory access failures or performance stalls. Debug valid/ready masks are full-width and should be read, not blindly written.

Test signals: SBTE transfer tests, interrupt/status decode tests, rate-limiter behavior, protection faults, and readback after masked configuration writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_sbte0_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_sbte0_mstr_if_axuser_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_sbte0_mstr_if_axuser_regs.h

Purpose: Defines AXUSER attribute register addresses for the `MME_SBTE0_MSTR_IF_AXUSER` DCORE0 master interface. The registers cover high-bandwidth and low-bandwidth ASID, MMU bypass, strong ordering, snoop, write-reduction, QoS, core, reserved, lock/coordination, and override fields at 0x40D1A80-0x40D1ACC.

Important APIs/types/functions: Exports 19 `mmDCORE0_*_AXUSER_*` address macros, including `mmDCORE0_MME_SBTE0_MSTR_IF_AXUSER_HB_ASID` (0x40D1A80), `mmDCORE0_MME_SBTE0_MSTR_IF_AXUSER_HB_MMU_BP` (0x40D1A84), `mmDCORE0_MME_SBTE0_MSTR_IF_AXUSER_HB_STRONG_ORDER` (0x40D1A88), `mmDCORE0_MME_SBTE0_MSTR_IF_AXUSER_HB_NO_SNOOP` (0x40D1A8C), `mmDCORE0_MME_SBTE0_MSTR_IF_AXUSER_HB_WR_REDUCTION` (0x40D1A90), and `mmDCORE0_MME_SBTE0_MSTR_IF_AXUSER_LB_OVRD` (0x40D1ACC). There are no functions or C types.

Control flow: Initialization, security, or firmware setup code writes these registers before the associated engine issues AXI transactions; runtime data movement then carries the programmed AXUSER attributes.

State and persistence behavior: Attribute values are hardware configuration state and persist until reset or reprogramming. The header itself is pure compile-time metadata.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. It integrates with MMU/security policy, cache/snoop behavior, and engine-specific DMA paths.

Risks: Incorrect ASID, MMU bypass, or strong-order settings can break isolation or memory ordering. Secured and nonsecured variants must not be interchanged.

Test signals: Security allowlist validation, MMU translation tests, protected/unprotected DMA smoke tests, and register readback of AXUSER setup for this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_sbte0_mstr_if_axuser_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_wb0_mstr_if_axuser_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_wb0_mstr_if_axuser_regs.h

Purpose: Defines AXUSER attribute register addresses for the `MME_WB0_MSTR_IF_AXUSER` DCORE0 master interface. The registers cover high-bandwidth and low-bandwidth ASID, MMU bypass, strong ordering, snoop, write-reduction, QoS, core, reserved, lock/coordination, and override fields at 0x40F9A80-0x40F9ACC.

Important APIs/types/functions: Exports 19 `mmDCORE0_*_AXUSER_*` address macros, including `mmDCORE0_MME_WB0_MSTR_IF_AXUSER_HB_ASID` (0x40F9A80), `mmDCORE0_MME_WB0_MSTR_IF_AXUSER_HB_MMU_BP` (0x40F9A84), `mmDCORE0_MME_WB0_MSTR_IF_AXUSER_HB_STRONG_ORDER` (0x40F9A88), `mmDCORE0_MME_WB0_MSTR_IF_AXUSER_HB_NO_SNOOP` (0x40F9A8C), `mmDCORE0_MME_WB0_MSTR_IF_AXUSER_HB_WR_REDUCTION` (0x40F9A90), and `mmDCORE0_MME_WB0_MSTR_IF_AXUSER_LB_OVRD` (0x40F9ACC). There are no functions or C types.

Control flow: Initialization, security, or firmware setup code writes these registers before the associated engine issues AXI transactions; runtime data movement then carries the programmed AXUSER attributes.

State and persistence behavior: Attribute values are hardware configuration state and persist until reset or reprogramming. The header itself is pure compile-time metadata.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. It integrates with MMU/security policy, cache/snoop behavior, and engine-specific DMA paths.

Risks: Incorrect ASID, MMU bypass, or strong-order settings can break isolation or memory ordering. Secured and nonsecured variants must not be interchanged.

Test signals: Security allowlist validation, MMU translation tests, protected/unprotected DMA smoke tests, and register readback of AXUSER setup for this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_wb0_mstr_if_axuser_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_rtr0_ctrl_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_rtr0_ctrl_regs.h

Purpose: Defines DCORE0 router control registers. The block maps memory count/map, read/write rate limits for memory/PCI/SRAM, reduction controls, SRAM and memory regulator tables, watchdog/shift/config registers, RAZWI decoder capture, and write-reduction counters at 0x4140100-0x4140BC4.

Important APIs/types/functions: Exports 134 `mmDCORE0_RTR0_CTRL_*` address macros. Repeated families include 16 SRAM tokens/latencies/bank IDs and 16 memory tokens/latencies/IDs, represented by `mmDCORE0_RTR0_CTRL_MEM_NUM` (0x4140100), `mmDCORE0_RTR0_CTRL_MEM_MAP` (0x4140104), `mmDCORE0_RTR0_CTRL_WR_RL_MEM` (0x4140108), `mmDCORE0_RTR0_CTRL_WR_RL_PCI` (0x414010C), `mmDCORE0_RTR0_CTRL_WR_RL_SRAM` (0x4140110), and `mmDCORE0_RTR0_CTRL_RGL_MEM_DEC_TOKEN_1` (0x4140BC4).

Control flow: Router initialization programs memory maps and regulator tables; runtime or debug code reads RAZWI and reduction counters after routing faults or performance investigations.

State and persistence behavior: Header state is absent. Hardware registers hold router configuration, rate-limit state, regulator tokens, error capture, and counters until reset or reprogramming.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. `gaudi2_security.c` references the router control base for protected region setup.

Risks: Rate-limit and memory-map mistakes can throttle or misroute traffic. RAZWI capture registers must be handled carefully so fault evidence is not lost before diagnostics.

Test signals: Router bring-up, memory-map validation, rate-limit tests, RAZWI fault injection/readback, and security-region coverage for the router control window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_rtr0_ctrl_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_rtr0_mstr_if_rr_prvt_hbw_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_rtr0_mstr_if_rr_prvt_hbw_regs.h

Purpose: Defines DCORE0 RTR0 master-interface range-register addresses for private HBW traffic. The block describes secured range minima/maxima, non-secured range minima/maxima, range masks, security-region configuration, decoders, access-error capture, and RAZWI error response at 0x4142200-0x4142378.

Important APIs/types/functions: Exports 95 `mmDCORE0_RTR0_MSTR_IF_RR_*` address macros, including `mmDCORE0_RTR0_MSTR_IF_RR_PRVT_HBW_SEC_RANGE_MIN_SHORT_LO_0` (0x4142200), `mmDCORE0_RTR0_MSTR_IF_RR_PRVT_HBW_SEC_RANGE_MIN_SHORT_LO_1` (0x4142204), `mmDCORE0_RTR0_MSTR_IF_RR_PRVT_HBW_SEC_RANGE_MIN_SHORT_LO_2` (0x4142208), `mmDCORE0_RTR0_MSTR_IF_RR_PRVT_HBW_SEC_RANGE_MIN_SHORT_LO_3` (0x414220C), `mmDCORE0_RTR0_MSTR_IF_RR_PRVT_HBW_SEC_RANGE_MIN_SHORT_LO_4` (0x4142210), and `mmDCORE0_RTR0_MSTR_IF_RR_PRVT_HBW_RAZWI_ERR_RESP` (0x4142378). There are no functions or C types.

Control flow: Security and address-decoder initialization writes allowed ranges and masks; runtime fault handling reads access-error and RAZWI registers when traffic violates the configured windows.

State and persistence behavior: The header has no software state. The hardware registers persist address-range policy and last-error information until reset or explicit writes.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. These range registers integrate with Gaudi2 security setup, router decode, and HBW/LBW fabric access paths.

Risks: Private/shared or HBW/LBW register windows are similarly named but enforce different traffic classes. Bad range masks can overexpose memory or block legitimate traffic.

Test signals: Secure/nonsecure access tests, range-boundary probes, RAZWI/error-response injection, and register dump comparison for the private HBW policy window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_rtr0_mstr_if_rr_prvt_hbw_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_rtr0_mstr_if_rr_prvt_lbw_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_rtr0_mstr_if_rr_prvt_lbw_regs.h

Purpose: Defines DCORE0 RTR0 master-interface range-register addresses for private LBW traffic. The block describes secured range minima/maxima, non-secured range minima/maxima, range masks, security-region configuration, decoders, access-error capture, and RAZWI error response at 0x4142600-0x4142748.

Important APIs/types/functions: Exports 83 `mmDCORE0_RTR0_MSTR_IF_RR_*` address macros, including `mmDCORE0_RTR0_MSTR_IF_RR_PRVT_LBW_SEC_RANGE_MIN_SHORT_0` (0x4142600), `mmDCORE0_RTR0_MSTR_IF_RR_PRVT_LBW_SEC_RANGE_MIN_SHORT_1` (0x4142604), `mmDCORE0_RTR0_MSTR_IF_RR_PRVT_LBW_SEC_RANGE_MIN_SHORT_2` (0x4142608), `mmDCORE0_RTR0_MSTR_IF_RR_PRVT_LBW_SEC_RANGE_MIN_SHORT_3` (0x414260C), `mmDCORE0_RTR0_MSTR_IF_RR_PRVT_LBW_SEC_RANGE_MIN_SHORT_4` (0x4142610), and `mmDCORE0_RTR0_MSTR_IF_RR_PRVT_LBW_RAZWI_ERR_RESP` (0x4142748). There are no functions or C types.

Control flow: Security and address-decoder initialization writes allowed ranges and masks; runtime fault handling reads access-error and RAZWI registers when traffic violates the configured windows.

State and persistence behavior: The header has no software state. The hardware registers persist address-range policy and last-error information until reset or explicit writes.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. These range registers integrate with Gaudi2 security setup, router decode, and HBW/LBW fabric access paths.

Risks: Private/shared or HBW/LBW register windows are similarly named but enforce different traffic classes. Bad range masks can overexpose memory or block legitimate traffic.

Test signals: Secure/nonsecure access tests, range-boundary probes, RAZWI/error-response injection, and register dump comparison for the private LBW policy window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_rtr0_mstr_if_rr_prvt_lbw_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_rtr0_mstr_if_rr_shrd_hbw_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_rtr0_mstr_if_rr_shrd_hbw_regs.h

Purpose: Defines DCORE0 RTR0 master-interface range-register addresses for shared HBW traffic. The block describes secured range minima/maxima, non-secured range minima/maxima, range masks, security-region configuration, decoders, access-error capture, and RAZWI error response at 0x4142000-0x4142178.

Important APIs/types/functions: Exports 95 `mmDCORE0_RTR0_MSTR_IF_RR_*` address macros, including `mmDCORE0_RTR0_MSTR_IF_RR_SHRD_HBW_SEC_RANGE_MIN_SHORT_LO_0` (0x4142000), `mmDCORE0_RTR0_MSTR_IF_RR_SHRD_HBW_SEC_RANGE_MIN_SHORT_LO_1` (0x4142004), `mmDCORE0_RTR0_MSTR_IF_RR_SHRD_HBW_SEC_RANGE_MIN_SHORT_LO_2` (0x4142008), `mmDCORE0_RTR0_MSTR_IF_RR_SHRD_HBW_SEC_RANGE_MIN_SHORT_LO_3` (0x414200C), `mmDCORE0_RTR0_MSTR_IF_RR_SHRD_HBW_SEC_RANGE_MIN_SHORT_LO_4` (0x4142010), and `mmDCORE0_RTR0_MSTR_IF_RR_SHRD_HBW_RAZWI_ERR_RESP` (0x4142178). There are no functions or C types.

Control flow: Security and address-decoder initialization writes allowed ranges and masks; runtime fault handling reads access-error and RAZWI registers when traffic violates the configured windows.

State and persistence behavior: The header has no software state. The hardware registers persist address-range policy and last-error information until reset or explicit writes.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. These range registers integrate with Gaudi2 security setup, router decode, and HBW/LBW fabric access paths.

Risks: Private/shared or HBW/LBW register windows are similarly named but enforce different traffic classes. Bad range masks can overexpose memory or block legitimate traffic.

Test signals: Secure/nonsecure access tests, range-boundary probes, RAZWI/error-response injection, and register dump comparison for the shared HBW policy window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_rtr0_mstr_if_rr_shrd_hbw_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_rtr0_mstr_if_rr_shrd_lbw_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_rtr0_mstr_if_rr_shrd_lbw_regs.h

Purpose: Defines DCORE0 RTR0 master-interface range-register addresses for shared LBW traffic. The block describes secured range minima/maxima, non-secured range minima/maxima, range masks, security-region configuration, decoders, access-error capture, and RAZWI error response at 0x4142400-0x4142548.

Important APIs/types/functions: Exports 83 `mmDCORE0_RTR0_MSTR_IF_RR_*` address macros, including `mmDCORE0_RTR0_MSTR_IF_RR_SHRD_LBW_SEC_RANGE_MIN_SHORT_0` (0x4142400), `mmDCORE0_RTR0_MSTR_IF_RR_SHRD_LBW_SEC_RANGE_MIN_SHORT_1` (0x4142404), `mmDCORE0_RTR0_MSTR_IF_RR_SHRD_LBW_SEC_RANGE_MIN_SHORT_2` (0x4142408), `mmDCORE0_RTR0_MSTR_IF_RR_SHRD_LBW_SEC_RANGE_MIN_SHORT_3` (0x414240C), `mmDCORE0_RTR0_MSTR_IF_RR_SHRD_LBW_SEC_RANGE_MIN_SHORT_4` (0x4142410), and `mmDCORE0_RTR0_MSTR_IF_RR_SHRD_LBW_RAZWI_ERR_RESP` (0x4142548). There are no functions or C types.

Control flow: Security and address-decoder initialization writes allowed ranges and masks; runtime fault handling reads access-error and RAZWI registers when traffic violates the configured windows.

State and persistence behavior: The header has no software state. The hardware registers persist address-range policy and last-error information until reset or explicit writes.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. These range registers integrate with Gaudi2 security setup, router decode, and HBW/LBW fabric access paths.

Risks: Private/shared or HBW/LBW register windows are similarly named but enforce different traffic classes. Bad range masks can overexpose memory or block legitimate traffic.

Test signals: Secure/nonsecure access tests, range-boundary probes, RAZWI/error-response injection, and register dump comparison for the shared LBW policy window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_rtr0_mstr_if_rr_shrd_lbw_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_sync_mngr_glbl_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_sync_mngr_glbl_masks.h

Purpose: Provides shift/mask constants for DCORE0 sync-manager global registers. It covers SEI overflow/unaligned/response-error fields, L2H masks, ASID/MMU-bypass controls, LBW delay and address/data fields, CQ base/size/PI/security/interrupt/inc-mode fields, and SOB-only enable.

Important APIs/types/functions: Exports 66 `DCORE0_SYNC_MNGR_GLBL_*` bitfield constants, represented by `DCORE0_SYNC_MNGR_GLBL_SM_SEI_MASK_SO_OVERFLOW_SHIFT` (0), `DCORE0_SYNC_MNGR_GLBL_SM_SEI_MASK_SO_OVERFLOW_MASK` (0x1), `DCORE0_SYNC_MNGR_GLBL_SM_SEI_MASK_MST_UNALIGN4B_SHIFT` (1), `DCORE0_SYNC_MNGR_GLBL_SM_SEI_MASK_MST_UNALIGN4B_MASK` (0x2), `DCORE0_SYNC_MNGR_GLBL_SM_SEI_MASK_MST_RSP_ERR_SHIFT` (2), and `DCORE0_SYNC_MNGR_GLBL_CQ_INC_MODE_MODE_MASK` (0x1). No executable code exists.

Control flow: Callers use these masks to pack writes and decode reads for the companion global sync-manager address header.

State and persistence behavior: The constants are compile-time metadata; they govern how software mutates or interprets live sync-manager register state.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. They pair with global sync-manager registers and queue/interrupt setup code.

Risks: Incorrect masks can break completion queues, interrupt routing, or security attributes. SEI cause fields should be cleared according to hardware semantics, not by arbitrary full-register writes.

Test signals: Bitfield encode/decode checks, CQ setup/readback, interrupt mask tests, SEI fault injection, and ASID/MMU-bypass validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_sync_mngr_glbl_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_sync_mngr_glbl_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_sync_mngr_glbl_regs.h

Purpose: Defines DCORE0 sync-manager global SOB registers. The map covers SEI mask/cause, L2H completion masks, ASID/security controls, LBW delay, producer-index sizing, CQ interrupt controls, 64 completion-queue base/size/PI/security/inc-mode entries, and 64 LBW address/data entries at 0x411E000-0x411E94C.

Important APIs/types/functions: Exports 590 `mmDCORE0_SYNC_MNGR_GLBL_*` address macros. Large repeated families include 64 CQ base-low/high, size, PI, security, increment-mode, and LBW address/data registers; representative macros are `mmDCORE0_SYNC_MNGR_GLBL_SM_SEI_MASK` (0x411E000), `mmDCORE0_SYNC_MNGR_GLBL_SM_SEI_CAUSE` (0x411E004), `mmDCORE0_SYNC_MNGR_GLBL_L2H_CPMR_L` (0x411E008), `mmDCORE0_SYNC_MNGR_GLBL_L2H_CPMR_H` (0x411E00C), `mmDCORE0_SYNC_MNGR_GLBL_L2H_MASK_L` (0x411E020), and `mmDCORE0_SYNC_MNGR_GLBL_CQ_INC_MODE_63` (0x411E94C).

Control flow: Driver setup configures sync-manager queues, security attributes, and interrupt masks; runtime synchronization objects and monitors drive CQ/LBW updates that software or firmware consumes.

State and persistence behavior: The header is stateless, while the registers hold live synchronization, CQ, interrupt, and LBW transaction state. Values persist until reset, queue teardown, or explicit reconfiguration.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. It integrates with sync-object/monitor object masks, command-completion queues, host interrupts, and security ASID policy.

Risks: Queue base/PI/size mistakes break completion delivery. Security and MMU-bypass fields affect isolation, and LBW address/data registers can generate unintended transactions if misprogrammed.

Test signals: Sync-manager queue setup, SOB/monitor completion tests, CQ interrupt delivery, ASID/security negative tests, LBW write/readback validation, and register dump decode for all 64 queue slots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_sync_mngr_glbl_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_sync_mngr_mstr_if_axuser_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_sync_mngr_mstr_if_axuser_masks.h

Purpose: Provides shift/mask constants for DCORE0 sync-manager AXUSER master-interface fields. It covers read/write ASID, MMU bypass, strong ordering, no-snoop, QoS, core, EMEM page, write-reduction, atomic read, reserved high/low bits, lock, coordinate, and override values.

Important APIs/types/functions: Exports 74 `DCORE0_SYNC_MNGR_MSTR_IF_AXUSER_*` field constants, represented by `DCORE0_SYNC_MNGR_MSTR_IF_AXUSER_HB_ASID_WR_SHIFT` (0), `DCORE0_SYNC_MNGR_MSTR_IF_AXUSER_HB_ASID_WR_MASK` (0x3FF), `DCORE0_SYNC_MNGR_MSTR_IF_AXUSER_HB_ASID_RD_SHIFT` (16), `DCORE0_SYNC_MNGR_MSTR_IF_AXUSER_HB_ASID_RD_MASK` (0x3FF0000), `DCORE0_SYNC_MNGR_MSTR_IF_AXUSER_HB_MMU_BP_WR_SHIFT` (0), and `DCORE0_SYNC_MNGR_MSTR_IF_AXUSER_LB_OVRD_VAL_MASK` (0xFFFFFFFF). There are no functions or types.

Control flow: No flow exists here. Callers combine these masks with `dcore0_sync_mngr_mstr_if_axuser_regs.h` addresses when packing AXUSER configuration writes.

State and persistence behavior: The constants are compile-time only; they control how driver writes mutate the sync-manager master-interface AXUSER hardware state.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. Integration is with sync-manager DMA/notification transactions and Gaudi2 security/MMU policy.

Risks: Incorrect bitfield packing can bypass the MMU, assign the wrong ASID, or set unintended ordering/cache attributes. Reserved-bit masks must remain synchronized with the hardware database.

Test signals: Bitfield encode/decode checks, AXUSER register readback, secured DMA tests, and negative tests for invalid ASID or MMU bypass policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_sync_mngr_mstr_if_axuser_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_sync_mngr_mstr_if_axuser_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_sync_mngr_mstr_if_axuser_regs.h

Purpose: Defines AXUSER attribute register addresses for the `SYNC_MNGR_MSTR_IF_AXUSER` DCORE0 master interface. The registers cover high-bandwidth and low-bandwidth ASID, MMU bypass, strong ordering, snoop, write-reduction, QoS, core, reserved, lock/coordination, and override fields at 0x411FA80-0x411FACC.

Important APIs/types/functions: Exports 19 `mmDCORE0_*_AXUSER_*` address macros, including `mmDCORE0_SYNC_MNGR_MSTR_IF_AXUSER_HB_ASID` (0x411FA80), `mmDCORE0_SYNC_MNGR_MSTR_IF_AXUSER_HB_MMU_BP` (0x411FA84), `mmDCORE0_SYNC_MNGR_MSTR_IF_AXUSER_HB_STRONG_ORDER` (0x411FA88), `mmDCORE0_SYNC_MNGR_MSTR_IF_AXUSER_HB_NO_SNOOP` (0x411FA8C), `mmDCORE0_SYNC_MNGR_MSTR_IF_AXUSER_HB_WR_REDUCTION` (0x411FA90), and `mmDCORE0_SYNC_MNGR_MSTR_IF_AXUSER_LB_OVRD` (0x411FACC). There are no functions or C types.

Control flow: Initialization, security, or firmware setup code writes these registers before the associated engine issues AXI transactions; runtime data movement then carries the programmed AXUSER attributes.

State and persistence behavior: Attribute values are hardware configuration state and persist until reset or reprogramming. The header itself is pure compile-time metadata.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. It integrates with MMU/security policy, cache/snoop behavior, and engine-specific DMA paths.

Risks: Incorrect ASID, MMU bypass, or strong-order settings can break isolation or memory ordering. Secured and nonsecured variants must not be interchanged.

Test signals: Security allowlist validation, MMU translation tests, protected/unprotected DMA smoke tests, and register readback of AXUSER setup for this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_sync_mngr_mstr_if_axuser_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_sync_mngr_objs_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_sync_mngr_objs_masks.h

Purpose: Defines bitfield shifts and masks for DCORE0 sync-manager object registers. It covers SOB object value/increment/long-SOB/trace-evict fields, monitor arm fields, monitor configuration, payload address/data, monitor status, security vectors, and privilege vectors.

Important APIs/types/functions: Exports 46 `DCORE0_SYNC_MNGR_OBJS_*` constants, including `DCORE0_SYNC_MNGR_OBJS_SOB_OBJ_VAL_SHIFT` (0), `DCORE0_SYNC_MNGR_OBJS_SOB_OBJ_VAL_MASK` (0x7FFF), `DCORE0_SYNC_MNGR_OBJS_SOB_OBJ_LONG_SOB_SHIFT` (24), `DCORE0_SYNC_MNGR_OBJS_SOB_OBJ_LONG_SOB_MASK` (0x1000000), `DCORE0_SYNC_MNGR_OBJS_SOB_OBJ_TRACE_EVICT_SHIFT` (30), and `DCORE0_SYNC_MNGR_OBJS_SM_PRIV_PRIV_MASK` (0xFFFFFFFF). It provides no functions or types.

Control flow: No code is executed here. Sync-object and monitor programming code uses these masks with the large object-register map to arm monitors, update SOBs, and decode pending/valid/protection state.

State and persistence behavior: The file has no state. Correct masks determine how software interacts with persistent SOB/monitor hardware state.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. It integrates with synchronization manager object programming, CQ/LBW monitor payloads, and security/privilege controls.

Risks: Incorrect monitor arm/config masks can miss completions or signal too early. Security and privilege vector fields are broad and should be programmed through validated policy paths.

Test signals: SOB increment/value tests, monitor arm and trigger tests, CQ/LBW payload tests, security/privilege negative tests, and register readback of packed object fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_sync_mngr_objs_masks.h -->
