# sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi/mpi30_image.h

## Purpose
`mpi30_image.h` defines the MPI 3.0 firmware/component image metadata ABI for Broadcom controllers. It describes component image headers, package/component manifests, secure-boot manifest elements, extended image headers, supported-device tables, encrypted hash/public-key data, and auxiliary processor data used by firmware update, validation, and image parsing paths.

## Important APIs, Types, And Functions
`struct mpi3_component_image_header` is the central image header. It records signatures, load address, data/start offsets, flash offsets and sizes, version/build/environment string offsets, application-specific data, CRC, flags, secondary flash offset, ETP data, RMC/ETP/security versions, component image version, hash-exclusion ranges, next image header offset, and reserved space. Associated macros define expected signatures, header offsets, header size, image type signatures, and flags for signed UEFI, certificate-chain format, device-key basis, signed NVDATA, activation requirement, compression, and flashability.

`struct mpi3_comp_image_version` stores build/customer IDs and phase/generation version bytes. `struct mpi3_hash_exclusion_format` defines ranges excluded from hashes. `struct mpi3_ci_manifest_mpi` and `struct mpi3_ci_manifest_mpi_comp_image_ref` describe package manifest metadata and component references. `struct mpi3_sb_manifest_mpi`, `struct mpi3_sb_manifest_element`, and related unions describe secure-boot manifest elements for component-image references, embedded keys, and diagnostic keys.

`struct mpi3_extended_image_header` describes non-component extended images by type, checksum, size, next offset, and identify string. `struct mpi3_supported_devices_data` and `struct mpi3_supported_device` list supported PCI IDs/revisions. `struct mpi3_encrypted_hash_data` and `struct mpi3_encrypted_hash_entry` carry hash algorithm, encryption algorithm, key/signature sizes, public key data, and paired-key flags. `struct mpi3_aux_processor_data` describes auxiliary processor boot method, type, version, load addresses, and payload.

## Control Flow
The header has no executable logic. A firmware-management path uses these layouts by scanning image headers, checking `signature0`/`signature1`/`signature2`, following `next_image_header_offset`, validating `header_size` and `crc`, consulting string offsets, applying hash-exclusion ranges, and interpreting flags before deciding whether an image is flashable, compressed, signed, or requires activation.

Manifest parsing uses `manifest_type` to distinguish classic MPI package manifests from secure-boot manifests, then walks component references, digest lists, embedded keys, diagnostic authorization keys, and flexible manifest elements. Extended-image parsing uses `image_type` to branch into NVDATA, supported-devices, encrypted-hash, RDE, auxiliary-processor, or product-specific payloads.

## State And Persistence
The structures model persistent firmware package contents and flash image metadata. They do not store kernel runtime state. Offsets in the structures are relative to image/package blobs and remain meaningful across firmware update operations. Security version, package version, component versions, keys, digests, and supported-device lists are persistent properties of the image being parsed or flashed.

## Dependencies And Integration Points
The header depends on little-endian kernel types and `union mpi3_version_union` from common MPI definitions. It integrates with `mpi3mr` firmware download/update code, package validation, secure boot and diagnostic authorization handling, supported-device checks, and any application-facing management interface that reports package metadata.

## Risks And Edge Cases
This is an on-media/on-wire image ABI. Incorrect endian conversion, offset arithmetic, flexible-array bounds, or signature checks can cause the driver to parse invalid data as trusted firmware metadata. Several arrays have default maxima of 1 unless overridden (`MPI3_CI_MANIFEST_MPI_MAX`, `MPI3_SUPPORTED_DEVICE_MAX`, `MPI3_PUBLIC_KEY_MAX`, `MPI3_ENCRYPTED_HASH_ENTRY_MAX`, `MPI3_AUX_PROC_DATA_MAX`), so consumers must use image sizes and element counts rather than fixed `sizeof` assumptions for real packages.

Security-sensitive fields include certificate-chain flags, device-key basis, security versions, digest arrays, key algorithms, diagnostic authorization keys, and public keys. Firmware update code must validate sizes, offsets, and algorithms before use and must not trust manifest counts without ensuring they remain inside the image buffer.

There is a spelling inconsistency in `MPI3_IMAGE_HASH_EXCUSION_NUM` and `MPI3_IMAGE_HEADER_ENVIROMENT_VAR_OFFSET_OFFSET`; consumers must use the existing macro names as ABI source constants despite the spelling.

## Test Signals
Tests should parse known-good and malformed firmware packages, validate component header offsets and `MPI3_IMAGE_HEADER_SIZE`, walk multi-component `next_image_header_offset` chains, verify CRC/hash exclusion handling, decode package version and build strings, reject unsupported signatures and out-of-range offsets, verify supported-device matching across vendor/device/revision masks, and exercise secure-boot manifest parsing for digest, embedded-key, diagnostic-key, and encrypted-hash elements.
