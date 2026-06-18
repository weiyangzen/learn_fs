# Research: sources/distributed-fs/seaweedfs/weed/s3api/object_lock_utils.go

## sources/distributed-fs/seaweedfs/weed/s3api/object_lock_utils.go

Purpose: shared utilities for bucket versioning and S3 Object Lock configuration/validation, used by S3 API handlers and Admin UI.

Important APIs: `StoreVersioningInExtended` and `GetVersioningStatus` persist versioning in filer `Entry.Extended`. `CreateObjectLockConfiguration`, `StoreObjectLockConfigurationInExtended`, `LoadObjectLockConfigurationFromExtended`, `ExtractObjectLockInfoFromConfig`, and `CreateObjectLockConfigurationFromParams` translate between UI parameters, XML structs, and extended attributes. `ValidateObjectLockParameters`, `ValidateRetention`, `ValidateLegalHold`, `ValidateObjectLockConfiguration`, and `validateDefaultRetention` enforce modes, future dates, duration bounds, and days-vs-years exclusivity. `HasObjectsWithActiveLocks` and `CheckBucketForLockedObjects` delegate scans to `s3_objectlock`.

State and persistence: bucket-level object-lock/versioning state is stored in filer extended keys such as enabled/default mode/default days/default years. Object-level validation uses request structs; locked-object scans traverse filer state through delegated package calls. Dependencies include S3 constants, filer proto entries, time, strconv, glog, and object-lock error/types defined elsewhere in `s3api`. Integration points are bucket create/configuration, retention/legal-hold handlers, delete-bucket protection, and Admin UI. Risks: years convert to 365-day UI duration, invalid stored numeric values are ignored, and nil retention/legal-hold inputs would panic if callers fail to validate before calling.
