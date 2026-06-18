# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/tags.go

## Purpose
This file defines the lifecycle package's object-tag extended-attribute prefix constant.

## Important APIs and state
`tagPrefix` is the string `X-Amz-Tagging-`. It is package-private, so it is intended for internal lifecycle code that reads or writes S3 object tag metadata from filer entry extended attributes.

## Control flow and persistence behavior
There is no control flow. Persistence behavior is implicit: object tags are represented as extended attributes whose keys use this prefix plus the tag key.

## Dependencies and integration points
The file has no imports. It aligns with S3 metadata constants and router tag extraction, which similarly reads extended attributes named with the S3 object tagging prefix.

## Risks and edge cases
Because the constant is private and this file is only three lines, drift is possible if other packages use a separate constant such as `s3_constants.AmzObjectTagging`. A future cleanup should avoid duplicate tag-prefix definitions or ensure all prefixes remain identical.

## Test signals
There are no direct tests for this file. Tag behavior is indirectly tested where lifecycle filtering and router `extractTags` are exercised.
