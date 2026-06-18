# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cloudsyncs3/src/libcloudsyncs3.c

## Purpose
Implements the S3 cloudsync plugin that downloads remote object contents via signed HTTP GET and writes them back into the GlusterFS file through the cloudsync recall path.

## Important APIs, types, and functions
Exports `store_ops` with download/init/reconfigure/fini hooks. `aws_private_t` stores hostname, bucket id, access key id, secret key, abort flag, and spinlock. `aws_init()` and `aws_reconfigure()` load S3 options. `aws_form_request()`, `aws_sign_request()`, and `aws_b64_encode()` build AWS Signature V2-style authorization. `aws_download_s3()` drives libcurl. `aws_write_callback()` copies downloaded chunks into iobufs and winds child `writev`; `aws_dlwritev_cbk()` sets abort on write failure.

## Control flow
Cloudsync calls `aws_download_s3(frame, config)` after stat repair finds a remote path. The plugin forms a resource string from bucket and `local->remotepath`, signs it, sets curl Date/Authorization headers and URL, streams response data into `aws_write_callback()`, and verifies HTTP 200. Each chunk is copied into an iobuf, written to `local->dlfd` at `local->dloffset`, and advances the offset.

## State and persistence behavior
Plugin config is in memory. The persistent effect is writing recalled bytes into the GlusterFS object through lower `writev`; cloudsync then removes remote/downloading xattrs. S3 credentials are kept in process memory and logged at debug in this snapshot.

## Dependencies and integration points
Depends on OpenSSL HMAC/BIO APIs, libcurl, GlusterFS iobuf/call-frame APIs, and the cloudsync plugin ABI. It does not implement `fop_remote_read`, so it supports recall/download, not direct remote reads.

## Risks and test signals
Risk signals include apparent bugs in this source snapshot: `aws_fini()` assigns `priv = (aws_private_t *)priv` instead of `config`, `aws_write_callback()` declares `dlfd` twice, and `aws_dlwritev_cbk()` treats `this->private` as `aws_private_t` although it is the translator private. Reconfigure overwrites strings without freeing old values. Tests should cover plugin load, missing credentials, signature generation vectors, curl non-200 responses, child write failure abort, large streaming recall, and fini/reconfigure leak detection.
