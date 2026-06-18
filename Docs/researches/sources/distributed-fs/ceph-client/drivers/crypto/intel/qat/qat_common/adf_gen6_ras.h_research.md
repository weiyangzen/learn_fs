# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen6_ras.h

Purpose: defines the Gen6 QAT reliability, availability, and serviceability register map used by the Gen6 RAS implementation. It is a hardware contract header: error-source registers, mask registers, parity status/control registers, CPP/RI/TI fault registers, ATU fault status, rate-limiting error bits, and generic status fields.

Important API: `adf_gen6_init_ras_ops(struct adf_ras_ops *ras_ops)` is the only function declaration. The rest of the file is symbolic register offsets and bit masks such as `ADF_GEN6_ERRSOU{0..3}`, `ADF_GEN6_ERRMSK{0..3}`, `ADF_GEN6_RIMEM_PARERR_FATAL_MASK`, `ADF_GEN6_CPP_CFC_FATAL_ERR_BIT`, and `ADF_GEN6_GENSTS_*`.

Control flow and state: no executable control flow or persistent state lives here. Runtime code includes this header to enable, mask, clear, classify, and report hardware error conditions. State is in device registers and `accel_dev->ras_errors` maintained elsewhere.

Dependencies and integration: depends on Linux `BIT()`/`GENMASK()` helpers. Integrates with Gen6 hardware data, ISR RAS dispatch, and sysfs RAS counters.

Risks and test signals: off-by-one or wrong-bit masks can misclassify fatal/nonfatal errors, suppress interrupts, or force unnecessary resets. Test via RAS interrupt injection, register readback after enable/disable, sysfs counter increments, and reset-required behavior.
