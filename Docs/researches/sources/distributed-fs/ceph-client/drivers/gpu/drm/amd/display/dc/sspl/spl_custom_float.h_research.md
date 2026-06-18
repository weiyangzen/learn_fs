# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/spl_custom_float.h

Purpose: this header declares the custom-float conversion API used by SPL register programming. It lets callers describe a compact floating-point format rather than hard-coding one register encoding into the math helper.

Important types and API: `struct spl_custom_float_format` contains `mantissa_bits`, `exponenta_bits`, and `sign`. `struct spl_custom_float_value` mirrors the decomposed result fields plus packed `value`, but the implementation's public API currently returns only the packed `uint32_t`. `spl_convert_to_custom_float_format()` accepts a fixed31_32 value, a format descriptor, and a result pointer.

Control flow and state: the header defines no state. Callers own the format descriptor and result storage; the implementation computes a one-shot conversion.

Dependencies and integration: it includes `spl_os_types.h` for kernel integer/bool types and namespace macros, and `spl_fixpt31_32.h` for the input value type. It is included by `dc_spl_types.h`, so the conversion API is available throughout SPL. Main integration is EASF matrix or coefficient-like register programming where custom exponent/mantissa encodings are required.

Risks and tests: there is no validation contract for legal bit widths in the header, so callers must avoid formats that produce invalid shifts or exceed the 32-bit result field. The misspelled `exponenta` field is part of the API and must be kept consistent. Tests should validate header/implementation agreement, namespace prefixing, and representative packed encodings for each hardware format that uses this helper.
