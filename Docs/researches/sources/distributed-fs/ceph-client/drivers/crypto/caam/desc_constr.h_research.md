<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/desc_constr.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/desc_constr.h

Purpose: inline helper library for constructing CAAM job and shared descriptors in memory with correct endian conversion, runtime pointer width, header length updates, jumps, immediate data, math commands, sequence pointers, and split-key protocol snippets.

Important APIs and control flow: `init_desc()`, `init_job_desc()`, `init_sh_desc()`, and PDB variants initialize descriptor headers. `desc_len()`, `desc_bytes()`, `desc_end()`, and `sh_desc_pdb()` inspect layout. `append_cmd()`, `append_ptr()`, `append_data()`, generated `append_key/load/fifo_load/fifo_store/operation/seq_*` helpers, `append_store()`, `set_jump_tgt_here()`, and math macros append command words and grow the header length. `desc_inline_query()` decides which data items fit inside a shared descriptor after reserving job descriptor space. `append_proto_dkp()` emits Derived Key Protocol commands for split HMAC keys.

State and persistence behavior: relies on global `caam_little_end` and `caam_ptr_sz`, initialized during controller probe, to encode pointers and u64 immediates. The descriptor buffer state is the header length word; helpers mutate it in place and do not allocate.

Dependencies and integration points: used by almost every CAAM algorithm path, RNG descriptors, QI shared descriptors, and PKC builders. Its pointer-width constants (`DESC_JOB_IO_LEN`, `MAX_SDLEN`) constrain QI shared descriptor size.

Risks and test signals: helpers do not bounds-check against `MAX_CAAM_DESCSIZE`, so callers must allocate enough words; wrong `caam_ptr_sz` corrupts descriptor layout; immediate-data helpers round lengths to words; command option combinations are mostly unchecked. Test signals include descriptor length matching bytes appended, correct 32/64-bit pointer encodings, DKP split-key generation, shared descriptor inline/reference decisions at boundary sizes, and CAAM hardware accepting descriptors without header/length errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/desc_constr.h -->
